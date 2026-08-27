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
            ]

            with mock.patch.object(sys, "argv", argv), redirect_stdout(output):
                self.assertEqual(MODULE.main(), 0)

        report = output.getvalue()
        self.assertEqual(report.count("cache_rate=75.0%"), 2)
        self.assertEqual(report.count("children=1"), 2)
        self.assertEqual(report.count("child_share=33.3%"), 2)

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


if __name__ == "__main__":
    unittest.main()
