---
name: codex-token-discipline
description: "Use for Codex work with clear excess-cost risk: broad or unpredictable logs and diffs, browser/UI loops, subagents, repeated compaction, or explicit usage audits. Guides preflight output limits, bounded delegation, evidence reuse, and compact checkpoints. Skip routine edits, direct answers, and ordinary test runs."
---

# Codex Token Discipline

## Purpose

Reduce total root-and-child cost without weakening task success, required evidence, or the requested deliverable.

Keep reads, tool output, retries, and delegation bounded. Preserve reusable evidence and escalate only the unresolved part.

## Operating Frame

Use only what changes behavior:

1. Name the current phase: explore, plan, implement, verify, publish, or handoff.
2. Define the next evidence needed before reading broadly.
3. Before a potentially noisy tool call, define the smallest useful return shape and output budget.
4. Delegate noisy side work only when it can return distilled findings with evidence.
5. At phase boundaries, save compact resume state and hand session-continuation decisions to the owning director when one exists.

Skip the ritual for small edits, direct answers, and simple commands.

## Preflight Output Contract

Prevent excess output before it enters the main context; do not rely on summarizing it afterward.

- For any unpredictable or batch command, name the required return shape first: status, count, paths, selected fields, or first actionable failure.
- Set a finite return budget on the tool call. For exec-family calls, default to an explicit budget at or below 2,000 tokens unless named evidence requires more; do not wait for a single large-output threshold.
- Filter, aggregate, or select at the source. For tests and builds, return the exit status, first actionable failure, and command before requesting more detail.
- When full output is useful for later inspection, write it to a task-local or temporary artifact and return only its path, size, compact summary, and first actionable failure. Inspect bounded slices from the artifact as needed.
- Do not create an artifact for disposable output that can be reduced at the source.

## Summary-First Reads

Start narrow; widen only when it changes the next decision.

- Search with `rg` or file lists before opening files.
- Prefer `git diff --stat`, `git diff --name-only`, focused `git diff -- <path>`, and targeted `sed -n` ranges before full diffs.
- For logs and command output, use `tail`, `head`, `jq`, counts, filters, or error searches before full transcripts.
- Treat every returned tool result as future input cost. Prefer counts, paths, summaries, or selected evidence before full output.
- After a failure, widen from the saved artifact or rerun only the smallest failing scope; avoid repeated full transcripts in the main thread.

If a broad read is necessary, state why and cap it to the smallest useful scope.

## Long-Running Work

Treat phase changes as context checkpoints.

- Before implementation or repo/task switches, preserve the conclusion, next decision, nearest next step, and smallest useful boundary.
- In repos using `project-context`, prefer `BRIEF.md` for compact current state and logs for evidence.
- When a director coordinates long-running work, report the checkpoint and let the director decide whether to continue, hand off, or rotate the session. Do not unconditionally prescribe or initiate a fresh session.
- Without a director, start fresh only when the saved surface is enough to continue and the user or owning workflow calls for it.

Do not store transcripts, validation matrices, or file inventories to compensate for a large conversation.

## Subagents

Delegation is not inherently cheaper. Use the narrowest named agent for bounded work that can return compact, independently useful evidence or output.

Start with one agent. Parallelize only independent, non-overlapping scopes. Do not duplicate the same investigation, keep agents alive after integration, or repeat still-valid validation.

Prompt with scope, write boundary, done condition, validation, and expected compact output. Children must not delegate.

## Browser And UI Loops

Before repeated visual or browser verification, write down the states to check.

- Prefer one screenshot or browser pass per named state.
- If a check fails, inspect the smallest owner: console error, DOM state, route data, or focused component.
- Keep images, base64 screenshots, full body text, and DOM dumps out of the main thread unless that artifact itself affects the next decision.
- Stop once the named states are verified or a concrete blocker is isolated.

## Always-Read Surfaces

Every line in global or repo instructions has recurring cost.

- Put durable behavior rules and safety boundaries in AGENTS-style files.
- Put repeatable workflows in skills.
- Put current task state in repo task docs.
- Put current reusable domain facts in reference docs.
- Remove stale profiles, duplicate instructions, and historical explanations instead of documenting around them.

When editing an always-read file, prefer a short routing rule over procedure text.

## Usage Audit

When asked where tokens went, resolve `scripts/summarize_codex_usage.py` relative to this installed skill directory, run it with `--help`, then audit with an explicit `--cwd-prefix`.

The script groups Codex rollout logs by root thread and reports token totals, cached-input rate, child-session token share, tool-output volume, large-output events, and top-output-tool signals without raw payloads.

Treat token totals as signals, not quality. Avoid home-wide text searches; point the script at `$CODEX_HOME/sessions` or another explicit sessions root.

## Final Check

- Did the main thread receive only the evidence needed for the current decision?
- Did noisy tool work have a return shape and budget before execution, with full detail kept in an artifact only when useful?
- Were large reads, browser loops, and subagents bounded by explicit questions?
- Is resumable state in the right surface, and did the owning director retain the continue/handoff/rotation decision?
- Did always-read guidance stay short and route detail elsewhere?
