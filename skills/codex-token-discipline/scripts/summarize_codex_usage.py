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


USAGE_KEYS = ("total_tokens", "input_tokens", "cached_input_tokens", "output_tokens", "reasoning_output_tokens")


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
    unknown_token_events: int = 0
    unknown_output_events: int = 0
    unknown_fork_boundary: bool = False
    output_by_tool: Counter[str] = field(default_factory=collections.Counter)
    output_results_by_tool: Counter[str] = field(default_factory=collections.Counter)
    model_usage: dict[tuple[str, str], Counter[str]] = field(default_factory=dict)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sessions-root", default="~/.codex/sessions")
    parser.add_argument("--cwd-prefix", required=True)
    parser.add_argument("--since-days", type=int, default=14)
    parser.add_argument("--since", help="Inclusive UTC/ISO-8601 token-event time (overrides --since-days).")
    parser.add_argument("--until", help="Exclusive UTC/ISO-8601 token-event time.")
    parser.add_argument("--top", type=int, default=15)
    return parser.parse_args()


def parse_time(value: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as error:
        raise argparse.ArgumentTypeError(f"invalid ISO-8601 timestamp: {value}") from error
    if parsed.tzinfo is None:
        raise argparse.ArgumentTypeError(f"timestamp needs an offset or Z: {value}")
    return parsed.astimezone(timezone.utc)


def event_time(obj: dict) -> datetime | None:
    value = obj.get("timestamp")
    if not isinstance(value, str):
        return None
    try:
        return parse_time(value)
    except argparse.ArgumentTypeError:
        return None


def in_window(value: datetime | None, since: datetime | None, until: datetime | None) -> bool:
    if since is None and until is None:
        return True
    return value is not None and (since is None or value >= since) and (until is None or value < until)


def iter_rollouts(root: Path) -> Iterable[Path]:
    """Yield every rollout; event timestamps, not filesystem mtime, define the window."""
    yield from root.glob("**/rollout-*.jsonl")


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
        return parent or ((meta.get("source") or {}).get("subagent") or {}).get("thread_spawn", {}).get("parent_thread_id")
    except AttributeError:
        return parent


def normalized_usage(raw: object) -> dict[str, int] | None:
    if not isinstance(raw, dict) or "total_tokens" not in raw:
        return None
    try:
        total_tokens = max(0, int(raw["total_tokens"] or 0))
    except (TypeError, ValueError):
        return None
    values = {}
    for key in USAGE_KEYS:
        if key == "total_tokens":
            values[key] = total_tokens
            continue
        try:
            values[key] = max(0, int(raw.get(key, 0) or 0))
        except (TypeError, ValueError):
            values[key] = 0
    return values


def usage_delta(current: dict[str, int], previous: dict[str, int] | None) -> dict[str, int]:
    """Turn cumulative snapshots into increments, treating a decrease as a reset."""
    if previous is None:
        return current
    if current["total_tokens"] < previous["total_tokens"]:
        return current
    return {key: max(0, current[key] - previous[key]) for key in USAGE_KEYS}


def add_usage(total: Counter[str], usage: dict[str, int], prefix: str = "") -> None:
    total[f"{prefix}total"] += usage.get("total_tokens", 0)
    total[f"{prefix}input"] += usage.get("input_tokens", 0)
    total[f"{prefix}cached"] += usage.get("cached_input_tokens", 0)
    total[f"{prefix}output"] += usage.get("output_tokens", 0)
    total[f"{prefix}reasoning"] += usage.get("reasoning_output_tokens", 0)


def parse_session(path: Path, meta: dict | None = None, since: datetime | None = None, until: datetime | None = None) -> Session | None:
    meta = meta or read_session_meta(path)
    if not meta:
        return None
    current_id = meta.get("id") or path.stem
    forked = parent_id(meta) is not None
    last_foreign_meta = -1
    previous_usage: dict[str, int] | None = None
    usage: Counter[str] = collections.Counter()
    calls = output_results = output_chars = max_output_chars = large_outputs = 0
    unknown_token_events = unknown_output_events = 0
    output_by_tool: Counter[str] = collections.Counter()
    output_results_by_tool: Counter[str] = collections.Counter()
    calls_by_id: dict[str, str] = {}
    model = effort = "unknown"
    model_usage: dict[tuple[str, str], Counter[str]] = collections.defaultdict(collections.Counter)
    try:
        with path.open(errors="ignore") as lines:
            for index, line in enumerate(lines):
                try:
                    obj = json.loads(line)
                except json.JSONDecodeError:
                    continue
                payload = obj.get("payload") or {}
                if forked and obj.get("type") == "session_meta" and payload.get("id") not in {None, current_id}:
                    last_foreign_meta = index
    except OSError:
        return None
    needs_child_boundary = forked and last_foreign_meta >= 0
    child_boundary_ready = not needs_child_boundary
    child_started = not needs_child_boundary
    try:
        lines = path.open(errors="ignore")
    except OSError:
        return None
    with lines:
        for index, line in enumerate(lines):
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue
            payload = obj.get("payload") or {}
            item_time = event_time(obj)
            if index <= last_foreign_meta:
                continue
            if not child_boundary_ready:
                if obj.get("type") == "event_msg" and payload.get("type") == "thread_settings_applied" and payload.get("thread_id") == current_id:
                    child_boundary_ready = True
                    previous_usage = None
                continue
            if not child_started:
                if obj.get("type") == "event_msg" and payload.get("type") == "token_count":
                    baseline = normalized_usage((payload.get("info") or {}).get("total_token_usage"))
                    if baseline is not None:
                        previous_usage = baseline
                elif obj.get("type") == "event_msg" and payload.get("type") == "task_started":
                    child_started = True
                    calls_by_id.clear()
                continue
            if obj.get("type") == "turn_context":
                model = str(payload.get("model") or "unknown")
                effort = str(payload.get("effort") or "unknown")
                continue
            if obj.get("type") == "event_msg" and payload.get("type") == "token_count":
                current = normalized_usage((payload.get("info") or {}).get("total_token_usage"))
                if current is None:
                    continue
                delta = usage_delta(current, previous_usage)
                previous_usage = current
                if not in_window(item_time, since, until):
                    if item_time is None and (since is not None or until is not None):
                        unknown_token_events += 1
                    continue
                for key, value in delta.items():
                    usage[key] += value
                    model_usage[(model, effort)][key] += value
                continue
            if obj.get("type") != "response_item":
                continue
            item_type = payload.get("type")
            if item_type in {"function_call", "custom_tool_call"}:
                if payload.get("call_id"):
                    calls_by_id[payload["call_id"]] = payload.get("name") or "custom"
                if in_window(item_time, since, until):
                    calls += 1
            elif item_type in {"function_call_output", "custom_tool_call_output"}:
                if not in_window(item_time, since, until):
                    if item_time is None and (since is not None or until is not None):
                        unknown_output_events += 1
                    continue
                tool_name = calls_by_id.get(payload.get("call_id"), "unknown")
                size = len(str(payload.get("output") or payload.get("content") or ""))
                output_results += 1
                output_chars += size
                max_output_chars = max(max_output_chars, size)
                output_by_tool[tool_name] += size
                output_results_by_tool[tool_name] += 1
                if size >= 50_000:
                    large_outputs += 1
    unknown_fork_boundary = needs_child_boundary and not child_started
    if not usage and not output_results and not calls and not unknown_token_events and not unknown_output_events and not unknown_fork_boundary:
        return None
    return Session(current_id, path, meta.get("cwd") or "", meta.get("timestamp") or "", parent_id(meta), dict(usage), calls, output_results, output_chars, max_output_chars, large_outputs, unknown_token_events, unknown_output_events, unknown_fork_boundary, output_by_tool, output_results_by_tool, dict(model_usage))


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


def add_child_usage(total: Counter[str], session: Session) -> None:
    add_usage(total, session.usage, "child_" if session.parent else "root_")
    if session.parent:
        total["children"] += 1


def add_session(total: Counter[str], session: Session) -> None:
    add_usage(total, session.usage)
    add_child_usage(total, session)
    total["sessions"] += 1
    total["calls"] += session.calls
    total["output_results"] += session.output_results
    total["output_chars"] += session.output_chars
    total["max_output_chars"] = max(total["max_output_chars"], session.max_output_chars)
    total["large_outputs"] += session.large_outputs
    total["unknown_token_events"] += session.unknown_token_events
    total["unknown_output_events"] += session.unknown_output_events
    total["unknown_fork_boundaries"] += int(session.unknown_fork_boundary)


def add_model_usage(total: dict[tuple[str, str], Counter[str]], session: Session) -> None:
    prefix = "child_" if session.parent else "root_"
    for model_effort, values in session.model_usage.items():
        for metric, value in values.items():
            total[model_effort][f"{prefix}{metric}"] += value


def format_tokens(value: int) -> str:
    return f"{value:,}"


def format_average(total: int, count: int) -> str:
    return format_tokens(total // count if count else 0)


def format_percentage(numerator: int, denominator: int) -> str:
    return f"{numerator / denominator:.1%}" if denominator else "n/a"


def format_top_outputs(output_by_tool: Counter[str], output_results_by_tool: Counter[str], limit: int = 3) -> str:
    return ";".join(f"{name}:chars={format_tokens(chars)},results={output_results_by_tool[name]},avg={format_average(chars, output_results_by_tool[name])}" for name, chars in output_by_tool.most_common(limit))


def format_model_usage(model_usage: dict[tuple[str, str], Counter[str]]) -> str:
    return ";".join(
        f"{model}/{effort}:root(input={format_tokens(values['root_input_tokens'])},cached={format_tokens(values['root_cached_input_tokens'])},output={format_tokens(values['root_output_tokens'])});child(input={format_tokens(values['child_input_tokens'])},cached={format_tokens(values['child_cached_input_tokens'])},output={format_tokens(values['child_output_tokens'])})"
        for (model, effort), values in sorted(model_usage.items())
    ) or "unknown"


def format_role_usage(totals: Counter[str]) -> str:
    return f"root=input={format_tokens(totals['root_input'])},cached={format_tokens(totals['root_cached'])},output={format_tokens(totals['root_output'])};child=input={format_tokens(totals['child_input'])},cached={format_tokens(totals['child_cached'])},output={format_tokens(totals['child_output'])}"


def main() -> int:
    args = parse_args()
    root = Path(args.sessions_root).expanduser()
    until = parse_time(args.until) if args.until else datetime.now(timezone.utc)
    since = parse_time(args.since) if args.since else until - timedelta(days=args.since_days)
    if until <= since:
        raise SystemExit("--until must be later than --since")
    cwd_prefix = Path(args.cwd_prefix).expanduser().resolve()
    rollout_meta = []
    parents: dict[str, str | None] = {}
    for path in iter_rollouts(root):
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
        session = parse_session(path, meta, since, until)
        if session:
            sessions[session.id] = session
            repo_names[session.id] = relative.parts[0] if relative.parts else cwd_prefix.name
    window = f"[{since.isoformat()}, {until.isoformat()})"
    if not sessions:
        print(f"No token events found for cwd prefix: {cwd_prefix} window={window}")
        return 0
    repo_totals: dict[str, Counter[str]] = collections.defaultdict(collections.Counter)
    repo_models: dict[str, dict[tuple[str, str], Counter[str]]] = collections.defaultdict(lambda: collections.defaultdict(collections.Counter))
    clusters: dict[str, list[Session]] = collections.defaultdict(list)
    for sid, session in sessions.items():
        repo_name = repo_names[sid]
        add_session(repo_totals[repo_name], session)
        add_model_usage(repo_models[repo_name], session)
        clusters[root_id(sid, parents)].append(session)
    print(f"Codex token usage window={window} cwd_prefix={cwd_prefix}")
    print("Deltas are assigned to their closing token event; a window edge can include work since the previous snapshot.")
    print("Missing event times are excluded and reported as unknown.")
    print("By repo:")
    for repo, totals in sorted(repo_totals.items(), key=lambda item: item[1]["total"], reverse=True):
        print(f"- {repo}: total={format_tokens(totals['total'])} uncached={format_tokens(totals['input'] - totals['cached'])} cache_rate={format_percentage(totals['cached'], totals['input'])} output={format_tokens(totals['output'])} sessions={totals['sessions']} children={totals['children']} child_share={format_percentage(totals['child_total'], totals['total'])} {format_role_usage(totals)} calls={totals['calls']} output_results={totals['output_results']} output_chars={format_tokens(totals['output_chars'])} avg_output_chars={format_average(totals['output_chars'], totals['output_results'])} max_output_chars={format_tokens(totals['max_output_chars'])} large_outputs={totals['large_outputs']} unknown_token_events={totals['unknown_token_events']} unknown_output_events={totals['unknown_output_events']} unknown_fork_boundaries={totals['unknown_fork_boundaries']}")
        print(f"  model_effort={format_model_usage(repo_models[repo])}")
    cluster_rows = []
    for root_value, members in clusters.items():
        totals: Counter[str] = collections.Counter()
        output_by_tool: Counter[str] = collections.Counter()
        output_results_by_tool: Counter[str] = collections.Counter()
        models: dict[tuple[str, str], Counter[str]] = collections.defaultdict(collections.Counter)
        repos: Counter[str] = collections.Counter()
        for session in members:
            add_session(totals, session)
            output_by_tool.update(session.output_by_tool)
            output_results_by_tool.update(session.output_results_by_tool)
            add_model_usage(models, session)
            repos[repo_names[session.id]] += 1
        cluster_rows.append((totals["total"], root_value, members, totals, output_by_tool, output_results_by_tool, models, repos))
    print(f"Top {min(args.top, len(cluster_rows))} task clusters:")
    for _, root_value, members, totals, output_by_tool, output_results_by_tool, models, repos in sorted(cluster_rows, reverse=True)[: args.top]:
        root_session = sessions.get(root_value) or members[0]
        print(f"- {root_session.timestamp} {root_value}: repos={dict(repos)} sessions={totals['sessions']} children={totals['children']} total={format_tokens(totals['total'])} uncached={format_tokens(totals['input'] - totals['cached'])} cache_rate={format_percentage(totals['cached'], totals['input'])} child_share={format_percentage(totals['child_total'], totals['total'])} {format_role_usage(totals)} output={format_tokens(totals['output'])} calls={totals['calls']} output_results={totals['output_results']} output_chars={format_tokens(totals['output_chars'])} avg_output_chars={format_average(totals['output_chars'], totals['output_results'])} max_output_chars={format_tokens(totals['max_output_chars'])} large_outputs={totals['large_outputs']} unknown_token_events={totals['unknown_token_events']} unknown_fork_boundaries={totals['unknown_fork_boundaries']}")
        print(f"  model_effort={format_model_usage(models)}")
        top_outputs = format_top_outputs(output_by_tool, output_results_by_tool)
        if top_outputs:
            print(f"  output_by_tool={top_outputs}")
        print(f"  {root_session.path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
