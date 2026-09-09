import importlib.util
import io
import json
import sys
import tempfile
import unittest
from collections import Counter
from contextlib import redirect_stdout
from pathlib import Path
from unittest import mock


SCRIPT = (
    Path(__file__).parents[1]
    / "skills"
    / "codex-token-discipline"
    / "scripts"
    / "summarize_codex_usage.py"
)
SPEC = importlib.util.spec_from_file_location("summarize_codex_usage", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class SummarizeCodexUsageTest(unittest.TestCase):
    def test_parse_session_counts_results_and_preserves_large_output_bucket(self):
        rows = [
            {
                "type": "session_meta",
                "payload": {
                    "id": "session-1",
                    "cwd": "/workspace/repo",
                    "timestamp": "2026-07-24T00:00:00Z",
                },
            },
            {
                "timestamp": "2026-08-13T00:00:10Z",
                "type": "event_msg",
                "payload": {
                    "type": "token_count",
                    "info": {
                        "total_token_usage": {
                            "total_tokens": 100,
                            "input_tokens": 80,
                            "cached_input_tokens": 20,
                            "output_tokens": 20,
                            "reasoning_output_tokens": 5,
                        }
                    },
                },
            },
            {
                "type": "session_meta",
                "payload": {
                    "id": "later-meta",
                    "cwd": "/different/workspace",
                    "timestamp": "2026-07-24T01:00:00Z",
                },
            },
            {
                "type": "response_item",
                "payload": {
                    "type": "function_call",
                    "name": "exec_command",
                    "call_id": "call-1",
                    "arguments": json.dumps({"cmd": "pytest", "max_output_tokens": 2000}),
                },
            },
            {
                "type": "response_item",
                "payload": {
                    "type": "function_call_output",
                    "call_id": "call-1",
                    "output": "x" * 50_000,
                },
            },
            {
                "type": "response_item",
                "payload": {
                    "type": "custom_tool_call_output",
                    "output": "unknown-output",
                },
            },
        ]

        with tempfile.TemporaryDirectory() as directory:
            rollout = Path(directory) / "rollout-test.jsonl"
            rollout.write_text("\n".join(json.dumps(row) for row in rows))
            session = MODULE.parse_session(rollout)

        self.assertIsNotNone(session)
        self.assertEqual(session.id, "session-1")
        self.assertEqual(session.output_results, 2)
        self.assertEqual(session.output_chars, 50_014)
        self.assertEqual(session.output_results_by_tool["exec_command"], 1)
        self.assertEqual(session.output_results_by_tool["unknown"], 1)
        self.assertEqual(session.large_outputs, 1)

    def test_parse_session_excludes_replayed_history_from_a_fork(self):
        rows = [
            {
                "type": "session_meta",
                "payload": {
                    "id": "child",
                    "cwd": "/workspace/repo",
                    "timestamp": "2026-08-20T07:49:49Z",
                    "forked_from_id": "parent",
                },
            },
            {
                "timestamp": "2026-08-13T00:01:10Z",
                "type": "event_msg",
                "payload": {
                    "type": "token_count",
                    "info": {"total_token_usage": {"total_tokens": 90}},
                },
            },
            {
                "type": "session_meta",
                "payload": {"id": "ancestor", "cwd": "/workspace/repo"},
            },
            {
                "type": "response_item",
                "payload": {
                    "type": "function_call",
                    "name": "inherited_tool",
                    "call_id": "inherited-call",
                },
            },
            {
                "type": "event_msg",
                "payload": {
                    "type": "token_count",
                    "info": {"total_token_usage": {"total_tokens": 100}},
                },
            },
            {
                "type": "session_meta",
                "payload": {"id": "parent", "cwd": "/workspace/repo"},
            },
            {
                "type": "event_msg",
                "payload": {
                    "type": "token_count",
                    "info": {"total_token_usage": {"total_tokens": 120}},
                },
            },
            {"type": "event_msg", "payload": {"type": "thread_settings_applied", "thread_id": "child"}},
            {
                "type": "event_msg",
                "payload": {
                    "type": "token_count",
                    "info": {"total_token_usage": {"total_tokens": 120}},
                },
            },
            {"type": "event_msg", "payload": {"type": "task_started"}},
            {
                "type": "response_item",
                "payload": {
                    "type": "function_call",
                    "name": "own_tool",
                    "call_id": "own-call",
                },
            },
            {
                "type": "response_item",
                "payload": {
                    "type": "function_call_output",
                    "call_id": "own-call",
                    "output": "own-output",
                },
            },
            {
                "type": "event_msg",
                "payload": {
                    "type": "token_count",
                    "info": {"total_token_usage": {"total_tokens": 170}},
                },
            },
        ]

        with tempfile.TemporaryDirectory() as directory:
            rollout = Path(directory) / "rollout-child.jsonl"
            rollout.write_text("\n".join(json.dumps(row) for row in rows))
            session = MODULE.parse_session(rollout)

        self.assertIsNotNone(session)
        self.assertEqual(session.id, "child")
        self.assertEqual(session.usage["total_tokens"], 50)
        self.assertEqual(session.calls, 1)
        self.assertEqual(session.output_results, 1)
        self.assertEqual(session.output_results_by_tool["own_tool"], 1)
        self.assertEqual(session.output_results_by_tool["inherited_tool"], 0)

    def test_format_top_outputs_reports_chars_result_count_and_average(self):
        formatted = MODULE.format_top_outputs(
            Counter({"exec_command": 16_000, "unknown": 12}),
            Counter({"exec_command": 2, "unknown": 1}),
        )

        self.assertEqual(
            formatted,
            "exec_command:chars=16,000,results=2,avg=8,000;unknown:chars=12,results=1,avg=12",
        )

    def test_format_percentage_reports_ratio_and_handles_zero_denominator(self):
        self.assertEqual(MODULE.format_percentage(95, 100), "95.0%")
        self.assertEqual(MODULE.format_percentage(0, 0), "n/a")

    def test_add_child_usage_counts_only_sessions_with_a_parent(self):
        totals = Counter()
        root = MODULE.Session(
            id="root",
            path=Path("root.jsonl"),
            cwd="/workspace/repo",
            timestamp="2026-08-13T00:00:00Z",
            parent=None,
            usage={"total_tokens": 80},
        )
        child = MODULE.Session(
            id="child",
            path=Path("child.jsonl"),
            cwd="/workspace/repo",
            timestamp="2026-08-13T00:01:00Z",
            parent="root",
            usage={"total_tokens": 20},
        )

        MODULE.add_child_usage(totals, root)
        MODULE.add_child_usage(totals, child)

        self.assertEqual(totals["children"], 1)
        self.assertEqual(totals["child_total"], 20)

    def test_main_reports_cache_rate_and_child_share_by_repo_and_cluster(self):
        root_rows = [
            {
                "type": "session_meta",
                "payload": {
                    "id": "root",
                    "cwd": "/workspace/repo",
                    "timestamp": "2026-08-13T00:00:00Z",
                },
            },
            {
                "timestamp": "2026-08-13T00:00:10Z",
                "type": "event_msg",
                "payload": {
                    "type": "token_count",
                    "info": {
                        "total_token_usage": {
                            "total_tokens": 100,
                            "input_tokens": 80,
                            "cached_input_tokens": 60,
                            "output_tokens": 20,
                        }
                    },
                },
            },
        ]
        child_rows = [
            {
                "type": "session_meta",
                "payload": {
                    "id": "child",
                    "cwd": "/workspace/repo",
                    "timestamp": "2026-08-13T00:01:00Z",
                    "forked_from_id": "root",
                },
            },
            {
                "timestamp": "2026-08-13T00:01:10Z",
                "type": "event_msg",
                "payload": {
                    "type": "token_count",
                    "info": {
                        "total_token_usage": {
                            "total_tokens": 50,
                            "input_tokens": 40,
                            "cached_input_tokens": 30,
                            "output_tokens": 10,
                        }
                    },
                },
            },
        ]

        with tempfile.TemporaryDirectory() as directory:
            sessions_root = Path(directory)
            (sessions_root / "rollout-root.jsonl").write_text(
                "\n".join(json.dumps(row) for row in root_rows)
            )
            (sessions_root / "rollout-child.jsonl").write_text(
                "\n".join(json.dumps(row) for row in child_rows)
            )
            output = io.StringIO()
            argv = [
                "summarize_codex_usage.py",
                "--sessions-root",
                str(sessions_root),
                "--cwd-prefix",
                "/workspace",
                "--since",
                "2026-08-13T00:00:00Z",
                "--until",
                "2026-08-14T00:00:00Z",
            ]

            with mock.patch.object(sys, "argv", argv), redirect_stdout(output):
                self.assertEqual(MODULE.main(), 0)

        report = output.getvalue()
        self.assertEqual(report.count("cache_rate=75.0%"), 2)
        self.assertEqual(report.count("children=1"), 2)
        self.assertEqual(report.count("child_share=33.3%"), 2)
        self.assertEqual(
            report.count("avg_output_chars=0 max_output_chars=0 large_outputs=0"), 2
        )
        self.assertIn(
            "model_effort=unknown/unknown:root(input=80,cached=60,output=20);child(input=40,cached=30,output=10)",
            report,
        )

    def test_relative_cwd_respects_directory_boundaries(self):
        prefix = Path("/workspace/repo")

        self.assertEqual(
            MODULE.relative_cwd("/workspace/repo/child", prefix), Path("child")
        )
        self.assertIsNone(MODULE.relative_cwd("/workspace/repo2", prefix))
        self.assertIsNone(MODULE.relative_cwd("", prefix))

    def test_root_id_follows_ancestors_outside_the_selected_prefix(self):
        parents = {
            "child": "outside-parent",
            "outside-parent": "outside-root",
            "outside-root": None,
        }

        self.assertEqual(MODULE.root_id("child", parents), "outside-root")

    def test_parse_session_uses_event_deltas_and_turn_context(self):
        rows = [
            {"type": "session_meta", "payload": {"id": "root", "cwd": "/workspace/repo"}},
            {"timestamp": "2026-09-01T00:00:00Z", "type": "turn_context", "payload": {"model": "one", "effort": "low"}},
            {"timestamp": "2026-09-01T00:00:01Z", "type": "event_msg", "payload": {"type": "token_count", "info": {"total_token_usage": {"total_tokens": 100, "input_tokens": 80, "cached_input_tokens": 40, "output_tokens": 20}}}},
            {"timestamp": "2026-09-01T00:00:02Z", "type": "turn_context", "payload": {"model": "two", "effort": "high"}},
            {"timestamp": "2026-09-01T00:00:03Z", "type": "event_msg", "payload": {"type": "token_count", "info": {"total_token_usage": {"total_tokens": 100, "input_tokens": 80, "cached_input_tokens": 40, "output_tokens": 20}}}},
            {"timestamp": "2026-09-01T00:00:04Z", "type": "event_msg", "payload": {"type": "token_count", "info": {"total_token_usage": {"total_tokens": 130, "input_tokens": 100, "cached_input_tokens": 50, "output_tokens": 30}}}},
            {"timestamp": "2026-09-01T00:00:04.500Z", "type": "event_msg", "payload": {"type": "token_count", "info": None}},
            {"timestamp": "2026-09-01T00:00:04.750Z", "type": "event_msg", "payload": {"type": "token_count", "info": {"total_token_usage": {}}}},
            {"timestamp": "2026-09-01T00:00:05Z", "type": "turn_context", "payload": {"model": "three", "effort": "medium"}},
            {"timestamp": "2026-09-01T00:00:06Z", "type": "event_msg", "payload": {"type": "token_count", "info": {"total_token_usage": {"total_tokens": 5, "input_tokens": 4, "cached_input_tokens": 1, "output_tokens": 1}}}},
        ]
        with tempfile.TemporaryDirectory() as directory:
            rollout = Path(directory) / "rollout-root.jsonl"
            rollout.write_text("\n".join(json.dumps(row) for row in rows))
            session = MODULE.parse_session(rollout, since=MODULE.parse_time("2026-09-01T00:00:02Z"), until=MODULE.parse_time("2026-09-01T00:00:07Z"))
        self.assertEqual(session.usage["total_tokens"], 35)
        self.assertEqual(session.model_usage[("two", "high")]["total_tokens"], 30)
        self.assertEqual(session.model_usage[("three", "medium")]["total_tokens"], 5)

    def test_parse_session_filters_tool_events_by_the_same_window(self):
        rows = [
            {"type": "session_meta", "payload": {"id": "root", "cwd": "/workspace/repo"}},
            {"timestamp": "2026-09-01T00:00:01Z", "type": "response_item", "payload": {"type": "function_call", "name": "exec", "call_id": "before"}},
            {"timestamp": "2026-09-01T00:00:02Z", "type": "response_item", "payload": {"type": "function_call_output", "call_id": "before", "output": "included"}},
            {"timestamp": "2026-09-01T00:00:03Z", "type": "response_item", "payload": {"type": "function_call", "name": "exec", "call_id": "after"}},
            {"timestamp": "2026-09-01T00:00:04Z", "type": "response_item", "payload": {"type": "function_call_output", "call_id": "after", "output": "excluded"}},
        ]
        with tempfile.TemporaryDirectory() as directory:
            rollout = Path(directory) / "rollout-root.jsonl"
            rollout.write_text("\n".join(json.dumps(row) for row in rows))
            session = MODULE.parse_session(rollout, since=MODULE.parse_time("2026-09-01T00:00:02Z"), until=MODULE.parse_time("2026-09-01T00:00:03Z"))
        self.assertEqual(session.calls, 0)
        self.assertEqual(session.output_results, 1)
        self.assertEqual(session.output_results_by_tool["exec"], 1)

    def test_parse_session_excludes_nested_fork_replay_until_last_ancestor_finishes(self):
        rows = [
            {"type": "session_meta", "payload": {"id": "child", "cwd": "/workspace/repo", "forked_from_id": "parent"}},
            {"type": "session_meta", "payload": {"id": "ancestor", "cwd": "/workspace/repo"}},
            {"type": "event_msg", "payload": {"type": "token_count", "info": {"total_token_usage": {"total_tokens": 90}}}},
            {"type": "event_msg", "payload": {"type": "task_started"}},
            {"type": "response_item", "payload": {"type": "function_call", "name": "ancestor_tool", "call_id": "ancestor"}},
            {"type": "session_meta", "payload": {"id": "parent", "cwd": "/workspace/repo"}},
            {"type": "event_msg", "payload": {"type": "token_count", "info": {"total_token_usage": {"total_tokens": 120}}}},
            {"type": "event_msg", "payload": {"type": "task_started"}},
            {"type": "response_item", "payload": {"type": "function_call", "name": "parent_tool", "call_id": "parent"}},
            {"type": "event_msg", "payload": {"type": "thread_settings_applied", "thread_id": "child"}},
            {"type": "event_msg", "payload": {"type": "token_count", "info": {"total_token_usage": {"total_tokens": 120}}}},
            {"type": "event_msg", "payload": {"type": "task_started"}},
            {"type": "response_item", "payload": {"type": "function_call", "name": "child_tool", "call_id": "child"}},
            {"type": "response_item", "payload": {"type": "function_call_output", "call_id": "child", "output": "own"}},
            {"type": "event_msg", "payload": {"type": "token_count", "info": {"total_token_usage": {"total_tokens": 130}}}},
        ]
        with tempfile.TemporaryDirectory() as directory:
            rollout = Path(directory) / "rollout-child.jsonl"
            rollout.write_text("\n".join(json.dumps(row) for row in rows))
            session = MODULE.parse_session(rollout)
        self.assertEqual(session.usage["total_tokens"], 10)
        self.assertEqual(session.calls, 1)
        self.assertEqual(session.output_results_by_tool["child_tool"], 1)
        self.assertEqual(session.output_results_by_tool["ancestor_tool"], 0)

    def test_parse_session_marks_a_fork_without_child_settings_as_unknown(self):
        rows = [
            {"type": "session_meta", "payload": {"id": "child", "cwd": "/workspace/repo", "forked_from_id": "parent"}},
            {"type": "session_meta", "payload": {"id": "parent", "cwd": "/workspace/repo"}},
            {"type": "event_msg", "payload": {"type": "token_count", "info": {"total_token_usage": {"total_tokens": 100}}}},
            {"type": "event_msg", "payload": {"type": "task_started"}},
            {"type": "event_msg", "payload": {"type": "token_count", "info": {"total_token_usage": {"total_tokens": 110}}}},
        ]
        with tempfile.TemporaryDirectory() as directory:
            rollout = Path(directory) / "rollout-child.jsonl"
            rollout.write_text("\n".join(json.dumps(row) for row in rows))
            session = MODULE.parse_session(rollout)
        self.assertTrue(session.unknown_fork_boundary)
        self.assertEqual(session.usage, {})


if __name__ == "__main__":
    unittest.main()
