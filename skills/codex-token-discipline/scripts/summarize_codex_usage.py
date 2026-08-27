#!/usr/bin/env python3
"""Summarize Codex rollout token usage for a cwd prefix."""

from __future__ import annotations

import argparse
import collections
import json
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Counter, Iterable


@dataclass
class Session:
    id: str
    path: Path
    cwd: str
    timestamp: str
    parent: str | None
    usage: dict[str, int]
    calls: int = 0
    output_results: int = 0
    output_chars: int = 0
    max_output_chars: int = 0
    large_outputs: int = 0
    output_by_tool: Counter[str] = field(default_factory=collections.Counter)
    output_results_by_tool: Counter[str] = field(default_factory=collections.Counter)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sessions-root", default="~/.codex/sessions")
    parser.add_argument("--cwd-prefix", required=True)
    parser.add_argument("--since-days", type=int, default=14)
    parser.add_argument("--top", type=int, default=15)
    return parser.parse_args()


def iter_rollouts(root: Path, since: datetime) -> Iterable[Path]:
    for path in root.glob("**/rollout-*.jsonl"):
        try:
            if datetime.fromtimestamp(path.stat().st_mtime, timezone.utc) < since:
                continue
        except OSError:
            continue
        yield path


def relative_cwd(path: str, prefix: Path) -> Path | None:
    if not path:
        return None
    try:
        return Path(path).expanduser().resolve().relative_to(prefix)
    except ValueError:
        return None


def read_session_meta(path: Path) -> dict | None:
    try:
        lines = path.open(errors="ignore")
    except OSError:
        return None
    with lines:
        for line in lines:
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue
            if obj.get("type") == "session_meta":
                payload = obj.get("payload")
                return payload if isinstance(payload, dict) else None
    return None


def parent_id(meta: dict) -> str | None:
    parent = meta.get("forked_from_id")
    try:
        return parent or ((meta.get("source") or {}).get("subagent") or {}).get(
            "thread_spawn", {}
        ).get("parent_thread_id")
    except AttributeError:
        return parent


def parse_session(path: Path, meta: dict | None = None) -> Session | None:
    meta = meta or read_session_meta(path)
    if not meta:
        return None
    current_id = meta.get("id") or path.stem
    forked = parent_id(meta) is not None
    usage = None
    baseline_usage = None
    waiting_for_child_start = False
    calls = 0
    output_results = 0
    output_chars = 0
    max_output_chars = 0
    large_outputs = 0
    output_by_tool: Counter[str] = collections.Counter()
    output_results_by_tool: Counter[str] = collections.Counter()
    calls_by_id: dict[str, str] = {}

    try:
        lines = path.open(errors="ignore")
    except OSError:
        return None

    with lines:
        for line in lines:
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue
            payload = obj.get("payload") or {}
            if obj.get("type") == "session_meta":
                if forked and payload.get("id") not in {None, current_id}:
                    # Fork rollouts replay ancestor history before the child's
                    # task_started event. Reset any provisional counts at each
                    # ancestor boundary so nested forks keep only child work.
                    usage = None
                    baseline_usage = None
                    waiting_for_child_start = True
                    calls = 0
                    output_results = 0
                    output_chars = 0
                    max_output_chars = 0
                    large_outputs = 0
                    output_by_tool.clear()
                    output_results_by_tool.clear()
                    calls_by_id.clear()
                continue
            if obj.get("type") == "event_msg" and payload.get("type") == "token_count":
                latest_usage = (payload.get("info") or {}).get("total_token_usage")
                if waiting_for_child_start:
                    baseline_usage = latest_usage or baseline_usage
                else:
                    usage = latest_usage or usage
                continue
            if obj.get("type") == "event_msg" and payload.get("type") == "task_started":
                if waiting_for_child_start:
                    usage = baseline_usage
                    waiting_for_child_start = False
                continue
            if waiting_for_child_start:
                continue
            if obj.get("type") != "response_item":
                continue
            item_type = payload.get("type")
            if item_type in {"function_call", "custom_tool_call"}:
                calls += 1
                name = payload.get("name") or "custom"
                if payload.get("call_id"):
                    calls_by_id[payload["call_id"]] = name
            elif item_type in {"function_call_output", "custom_tool_call_output"}:
                tool_name = calls_by_id.get(payload.get("call_id"), "unknown")
                size = len(str(payload.get("output") or payload.get("content") or ""))
                output_results += 1
                output_chars += size
                max_output_chars = max(max_output_chars, size)
                output_by_tool[tool_name] += size
                output_results_by_tool[tool_name] += 1
                if size >= 50_000:
                    large_outputs += 1

    if not usage:
        return None

    usage_keys = (
        "total_tokens",
        "input_tokens",
        "cached_input_tokens",
        "output_tokens",
        "reasoning_output_tokens",
    )
    exclusive_usage = {
        key: max(
            0,
            int(usage.get(key, 0) or 0)
            - int((baseline_usage or {}).get(key, 0) or 0),
        )
        for key in usage_keys
    }

    return Session(
        id=current_id,
        path=path,
        cwd=meta.get("cwd") or "",
        timestamp=meta.get("timestamp") or "",
        parent=parent_id(meta),
        usage=exclusive_usage,
        calls=calls,
        output_results=output_results,
        output_chars=output_chars,
        max_output_chars=max_output_chars,
        large_outputs=large_outputs,
        output_by_tool=output_by_tool,
        output_results_by_tool=output_results_by_tool,
    )


def root_id(session_id: str, parents: dict[str, str | None]) -> str:
    seen: set[str] = set()
    current = session_id
    while current not in seen:
        seen.add(current)
        parent = parents.get(current)
        if not parent:
            return current
        current = parent
    return current


def add_usage(total: Counter[str], usage: dict[str, int]) -> None:
    total["total"] += usage.get("total_tokens", 0)
    total["input"] += usage.get("input_tokens", 0)
    total["cached"] += usage.get("cached_input_tokens", 0)
    total["output"] += usage.get("output_tokens", 0)
    total["reasoning"] += usage.get("reasoning_output_tokens", 0)


def format_tokens(value: int) -> str:
    return f"{value:,}"


def format_average(total: int, count: int) -> str:
    return format_tokens(total // count if count else 0)


def format_percentage(numerator: int, denominator: int) -> str:
    return f"{numerator / denominator:.1%}" if denominator else "n/a"


def add_child_usage(total: Counter[str], session: Session) -> None:
    if session.parent:
        total["children"] += 1
        total["child_total"] += session.usage.get("total_tokens", 0)


def format_top_outputs(
    output_by_tool: Counter[str], output_results_by_tool: Counter[str], limit: int = 3
) -> str:
    parts = []
    for name, chars in output_by_tool.most_common(limit):
        results = output_results_by_tool[name]
        parts.append(
            f"{name}:chars={format_tokens(chars)},results={results},avg={format_average(chars, results)}"
        )
    return ";".join(parts)


def main() -> int:
    args = parse_args()
    root = Path(args.sessions_root).expanduser()
    since = datetime.now(timezone.utc) - timedelta(days=args.since_days)
    cwd_prefix = Path(args.cwd_prefix).expanduser().resolve()

    rollout_meta = []
    parents: dict[str, str | None] = {}
    for path in iter_rollouts(root, since):
        meta = read_session_meta(path)
        if not meta:
            continue
        session_id = meta.get("id") or path.stem
        parents[session_id] = parent_id(meta)
        relative = relative_cwd(meta.get("cwd") or "", cwd_prefix)
        if relative is not None:
            rollout_meta.append((path, meta, relative))

    sessions = {}
    repo_names = {}
    for path, meta, relative in rollout_meta:
        session = parse_session(path, meta)
        if session:
            sessions[session.id] = session
            repo_names[session.id] = relative.parts[0] if relative.parts else cwd_prefix.name

    if not sessions:
        print(f"No sessions found for cwd prefix: {cwd_prefix}")
        return 0

    repo_totals: dict[str, Counter[str]] = collections.defaultdict(collections.Counter)
    clusters: dict[str, list[Session]] = collections.defaultdict(list)
    for sid, session in sessions.items():
        repo_name = repo_names[sid]
        totals = repo_totals[repo_name]
        add_usage(totals, session.usage)
        totals["sessions"] += 1
        totals["calls"] += session.calls
        totals["output_results"] += session.output_results
        totals["output_chars"] += session.output_chars
        totals["max_output_chars"] = max(totals["max_output_chars"], session.max_output_chars)
        totals["large_outputs"] += session.large_outputs
        add_child_usage(totals, session)
        clusters[root_id(sid, parents)].append(session)

    print(f"Codex token usage since {since.date()} for {cwd_prefix}")
    print()
    print("By repo:")
    for repo, totals in sorted(repo_totals.items(), key=lambda item: item[1]["total"], reverse=True):
        uncached = totals["input"] - totals["cached"]
        cache_rate = format_percentage(totals["cached"], totals["input"])
        child_share = format_percentage(totals["child_total"], totals["total"])
        print(
            f"- {repo}: total={format_tokens(totals['total'])} "
            f"uncached={format_tokens(uncached)} cache_rate={cache_rate} output={format_tokens(totals['output'])} "
            f"sessions={totals['sessions']} children={totals['children']} child_share={child_share} "
            f"calls={totals['calls']} output_results={totals['output_results']} "
            f"output_chars={format_tokens(totals['output_chars'])} avg_output_chars={format_average(totals['output_chars'], totals['output_results'])} "
            f"max_output_chars={format_tokens(totals['max_output_chars'])} large_outputs={totals['large_outputs']}"
        )

    cluster_rows = []
    for root, members in clusters.items():
        totals: Counter[str] = collections.Counter()
        output_by_tool: Counter[str] = collections.Counter()
        output_results_by_tool: Counter[str] = collections.Counter()
        repos: Counter[str] = collections.Counter()
        for session in members:
            add_usage(totals, session.usage)
            totals["sessions"] += 1
            totals["calls"] += session.calls
            totals["output_results"] += session.output_results
            totals["output_chars"] += session.output_chars
            totals["max_output_chars"] = max(totals["max_output_chars"], session.max_output_chars)
            totals["large_outputs"] += session.large_outputs
            add_child_usage(totals, session)
            output_by_tool.update(session.output_by_tool)
            output_results_by_tool.update(session.output_results_by_tool)
            repos[repo_names[session.id]] += 1
        cluster_rows.append((totals["total"], root, members, totals, output_by_tool, output_results_by_tool, repos))

    print()
    print(f"Top {min(args.top, len(cluster_rows))} task clusters:")
    for _, root, members, totals, output_by_tool, output_results_by_tool, repos in sorted(cluster_rows, reverse=True)[: args.top]:
        root_session = sessions.get(root) or members[0]
        uncached = totals["input"] - totals["cached"]
        cache_rate = format_percentage(totals["cached"], totals["input"])
        child_share = format_percentage(totals["child_total"], totals["total"])
        top_outputs = format_top_outputs(output_by_tool, output_results_by_tool)
        print(
            f"- {root_session.timestamp} {root}: repos={dict(repos)} sessions={totals['sessions']} "
            f"children={totals['children']} total={format_tokens(totals['total'])} "
            f"uncached={format_tokens(uncached)} cache_rate={cache_rate} child_share={child_share} "
            f"output={format_tokens(totals['output'])} calls={totals['calls']} output_results={totals['output_results']} "
            f"output_chars={format_tokens(totals['output_chars'])} avg_output_chars={format_average(totals['output_chars'], totals['output_results'])} "
            f"max_output_chars={format_tokens(totals['max_output_chars'])} large_outputs={totals['large_outputs']}"
        )
        if top_outputs:
            print(f"  output_by_tool={top_outputs}")
        print(f"  {root_session.path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
