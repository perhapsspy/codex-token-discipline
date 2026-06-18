#!/usr/bin/env python3
"""Summarize Codex rollout token usage for a cwd prefix."""

from __future__ import annotations

import argparse
import collections
import json
import re
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
    token_events: int = 0
    calls: int = 0
    output_chars: int = 0
    max_output_chars: int = 0
    metrics: Counter[str] = field(default_factory=collections.Counter)
    call_names: Counter[str] = field(default_factory=collections.Counter)
    output_by_tool: Counter[str] = field(default_factory=collections.Counter)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sessions-root", default="~/.codex/sessions")
    parser.add_argument("--cwd-prefix", required=True)
    parser.add_argument("--since-days", type=int, default=14)
    parser.add_argument("--top", type=int, default=15)
    return parser.parse_args()


def parse_timestamp(value: str) -> datetime | None:
    if not value:
        return None
    try:
        if value.endswith("Z"):
            value = value[:-1] + "+00:00"
        return datetime.fromisoformat(value)
    except ValueError:
        return None


def iter_rollouts(root: Path, since: datetime) -> Iterable[Path]:
    for path in root.glob("**/rollout-*.jsonl"):
        try:
            if datetime.fromtimestamp(path.stat().st_mtime, timezone.utc) < since:
                continue
        except OSError:
            continue
        yield path


def parse_session(path: Path) -> Session | None:
    meta = None
    usage = None
    token_events = 0
    calls = 0
    output_chars = 0
    max_output_chars = 0
    metrics: Counter[str] = collections.Counter()
    call_names: Counter[str] = collections.Counter()
    output_by_tool: Counter[str] = collections.Counter()
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
                meta = payload
                continue
            if obj.get("type") == "event_msg" and payload.get("type") == "token_count":
                token_events += 1
                usage = (payload.get("info") or {}).get("total_token_usage") or usage
                continue
            if obj.get("type") != "response_item":
                continue
            item_type = payload.get("type")
            if item_type in {"function_call", "custom_tool_call"}:
                calls += 1
                name = payload.get("name") or "custom"
                call_names[name] += 1
                if payload.get("call_id"):
                    calls_by_id[payload["call_id"]] = name
                collect_call_metrics(name, payload.get("arguments") or "", metrics)
            elif item_type in {"function_call_output", "custom_tool_call_output"}:
                tool_name = calls_by_id.get(payload.get("call_id"), "unknown")
                size = len(str(payload.get("output") or payload.get("content") or ""))
                output_chars += size
                max_output_chars = max(max_output_chars, size)
                output_by_tool[tool_name] += size
                if size >= 500_000:
                    metrics["output_500k"] += 1
                elif size >= 100_000:
                    metrics["output_100k"] += 1
                elif size >= 50_000:
                    metrics["output_50k"] += 1

    if not meta or not usage:
        return None

    parent = meta.get("forked_from_id")
    try:
        parent = parent or ((meta.get("source") or {}).get("subagent") or {}).get("thread_spawn", {}).get("parent_thread_id")
    except AttributeError:
        pass

    return Session(
        id=meta.get("id") or path.stem,
        path=path,
        cwd=meta.get("cwd") or "",
        timestamp=meta.get("timestamp") or "",
        parent=parent,
        usage={key: int(usage.get(key, 0) or 0) for key in ("total_tokens", "input_tokens", "cached_input_tokens", "output_tokens", "reasoning_output_tokens")},
        token_events=token_events,
        calls=calls,
        output_chars=output_chars,
        max_output_chars=max_output_chars,
        metrics=metrics,
        call_names=call_names,
        output_by_tool=output_by_tool,
    )


def collect_call_metrics(name: str, args: str, metrics: Counter[str]) -> None:
    if name == "spawn_agent":
        metrics["spawn"] += 1
    if name == "wait_agent":
        metrics["wait"] += 1
    if name == "view_image":
        metrics["view_image"] += 1
    if name == "js":
        metrics["js"] += 1
        if "screenshot" in args or "emitImage" in args:
            metrics["browser_image"] += 1
        if "innerText" in args or "document.body" in args or "outerHTML" in args:
            metrics["dom_or_body_dump"] += 1
    if name != "exec_command":
        return
    try:
        parsed = json.loads(args)
    except json.JSONDecodeError:
        return
    if not isinstance(parsed, dict):
        return
    cmd = parsed.get("cmd") or ""
    max_output_tokens = parsed.get("max_output_tokens")
    if isinstance(max_output_tokens, int) and max_output_tokens >= 20_000:
        metrics["large_output_budget"] += 1
    if re.search(r"(^|\s)rg\s", cmd):
        metrics["rg"] += 1
    if re.search(r"(^|\s)sed\s", cmd):
        metrics["sed"] += 1
    if re.search(r"(^|\s)git\s", cmd):
        metrics["git"] += 1
    if re.search(r"\b(bun|npm|pnpm|yarn|pytest|cargo|go|just)\b", cmd):
        metrics["test_or_build"] += 1
    if "kubectl" in cmd:
        metrics["kubectl"] += 1
    if re.search(r"(^|\s)find\s+/(Users|home|var|tmp)\b", cmd) or re.search(r"(^|\s)rg\s+.*\s/(Users|home)\b", cmd):
        metrics["broad_abs_search"] += 1


def root_id(session_id: str, sessions: dict[str, Session]) -> str:
    seen: set[str] = set()
    current = session_id
    while current not in seen:
        seen.add(current)
        parent = sessions.get(current).parent if current in sessions else None
        if not parent or parent not in sessions:
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


def main() -> int:
    args = parse_args()
    root = Path(args.sessions_root).expanduser()
    since = datetime.now(timezone.utc) - timedelta(days=args.since_days)
    cwd_prefix = str(Path(args.cwd_prefix).expanduser())

    sessions = {}
    for path in iter_rollouts(root, since):
        session = parse_session(path)
        if session:
            sessions[session.id] = session

    selected = {sid: session for sid, session in sessions.items() if session.cwd.startswith(cwd_prefix)}
    if not selected:
        print(f"No sessions found for cwd prefix: {cwd_prefix}")
        return 0

    repo_totals: dict[str, Counter[str]] = collections.defaultdict(collections.Counter)
    clusters: dict[str, list[Session]] = collections.defaultdict(list)
    for sid, session in selected.items():
        repo_name = session.cwd.removeprefix(cwd_prefix).strip("/").split("/", 1)[0] or Path(cwd_prefix).name
        totals = repo_totals[repo_name]
        add_usage(totals, session.usage)
        totals["sessions"] += 1
        totals["token_events"] += session.token_events
        totals["calls"] += session.calls
        totals["output_chars"] += session.output_chars
        totals["max_output_chars"] = max(totals["max_output_chars"], session.max_output_chars)
        totals.update(session.metrics)
        clusters[root_id(sid, sessions)].append(session)

    print(f"Codex token usage since {since.date()} for {cwd_prefix}")
    print()
    print("By repo:")
    for repo, totals in sorted(repo_totals.items(), key=lambda item: item[1]["total"], reverse=True):
        uncached = totals["input"] - totals["cached"]
        print(
            f"- {repo}: total={format_tokens(totals['total'])} "
            f"uncached={format_tokens(uncached)} output={format_tokens(totals['output'])} "
            f"sessions={totals['sessions']} calls={totals['calls']} output_chars={format_tokens(totals['output_chars'])} "
            f"max_output_chars={format_tokens(totals['max_output_chars'])} large_outputs={totals['output_50k'] + totals['output_100k'] + totals['output_500k']} "
            f"browser_image={totals['browser_image']} dom_dump={totals['dom_or_body_dump']} spawn={totals['spawn']}"
        )

    cluster_rows = []
    for root, members in clusters.items():
        totals: Counter[str] = collections.Counter()
        metrics: Counter[str] = collections.Counter()
        output_by_tool: Counter[str] = collections.Counter()
        repos: Counter[str] = collections.Counter()
        for session in members:
            add_usage(totals, session.usage)
            totals["sessions"] += 1
            totals["token_events"] += session.token_events
            totals["calls"] += session.calls
            totals["output_chars"] += session.output_chars
            totals["max_output_chars"] = max(totals["max_output_chars"], session.max_output_chars)
            metrics.update(session.metrics)
            output_by_tool.update(session.output_by_tool)
            repos[session.cwd.removeprefix(cwd_prefix).strip("/").split("/", 1)[0] or Path(cwd_prefix).name] += 1
        cluster_rows.append((totals["total"], root, members, totals, metrics, output_by_tool, repos))

    print()
    print(f"Top {min(args.top, len(cluster_rows))} task clusters:")
    for _, root, members, totals, metrics, output_by_tool, repos in sorted(cluster_rows, reverse=True)[: args.top]:
        root_session = sessions.get(root) or members[0]
        uncached = totals["input"] - totals["cached"]
        top_outputs = ",".join(f"{name}:{format_tokens(chars)}" for name, chars in output_by_tool.most_common(3))
        print(
            f"- {root_session.timestamp} {root}: repos={dict(repos)} sessions={totals['sessions']} "
            f"total={format_tokens(totals['total'])} uncached={format_tokens(uncached)} "
            f"output={format_tokens(totals['output'])} calls={totals['calls']} output_chars={format_tokens(totals['output_chars'])} "
            f"max_output_chars={format_tokens(totals['max_output_chars'])} large_outputs={metrics['output_50k'] + metrics['output_100k'] + metrics['output_500k']} "
            f"large_output_budget={metrics['large_output_budget']} browser_image={metrics['browser_image']} dom_dump={metrics['dom_or_body_dump']} "
            f"broad_abs_search={metrics['broad_abs_search']} sed={metrics['sed']} rg={metrics['rg']} spawn={metrics['spawn']}"
        )
        if top_outputs:
            print(f"  output_by_tool={top_outputs}")
        print(f"  {root_session.path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
