import importlib.util
import json
import sys
import tempfile
import unittest
from collections import Counter
from pathlib import Path


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
        self.assertEqual(session.output_results, 2)
        self.assertEqual(session.output_chars, 50_014)
        self.assertEqual(session.output_results_by_tool["exec_command"], 1)
        self.assertEqual(session.output_results_by_tool["unknown"], 1)
        self.assertEqual(session.metrics["output_50k"], 1)

    def test_format_top_outputs_reports_chars_result_count_and_average(self):
        formatted = MODULE.format_top_outputs(
            Counter({"exec_command": 16_000, "unknown": 12}),
            Counter({"exec_command": 2, "unknown": 1}),
        )

        self.assertEqual(
            formatted,
            "exec_command:chars=16,000,results=2,avg=8,000;unknown:chars=12,results=1,avg=12",
        )

    def test_exec_pragma_large_budget_is_counted(self):
        metrics = Counter()

        MODULE.collect_call_metrics(
            "exec", '// @exec: {"yield_time_ms": 10000, "max_output_tokens": 20000}', metrics
        )

        self.assertEqual(metrics["large_output_budget"], 1)


if __name__ == "__main__":
    unittest.main()
