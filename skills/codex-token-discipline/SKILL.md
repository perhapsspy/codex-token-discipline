---
name: codex-token-discipline
description: "Use for high-token-risk Codex work: long sessions, broad reads/diffs/logs, browser/UI loops, subagents, always-read changes, or token audits. Guides summary-first reads, bounded delegation, compact resume state, and usage audits."
---

# Codex Token Discipline

## Purpose

Keep long Codex work effective without letting noisy reads, repeated large outputs, broad delegation, or bulky always-read instructions crowd the context. This controls intermediate work, not final-answer depth.

## Operating Frame

Use only what changes behavior:

1. Name the current phase: explore, plan, implement, verify, publish, or handoff.
2. Define the next evidence needed before reading broadly.
3. Prefer summaries and bounded reads before full files, diffs, logs, screenshots, or command output.
4. Delegate noisy side work only when it can return distilled findings with evidence.
5. At phase boundaries, save compact resume state before continuing or starting fresh.

Skip the ritual for small edits, direct answers, and simple commands.

## Summary-First Reads

Start narrow; widen only when it changes the next decision.

- Search with `rg` or file lists before opening files.
- Prefer `git diff --stat`, `git diff --name-only`, focused `git diff -- <path>`, and targeted `sed -n` ranges before full diffs.
- For logs and command output, use `tail`, `head`, `jq`, counts, filters, or error searches before full transcripts.
- For generated or test output, keep the first actionable failure and command; avoid repeated full reruns in the main thread.
- Treat large tool results as future input cost. For commands likely to exceed about 10k chars, ask for counts, paths, summaries, or the first actionable failure before full output.
- Raise output budgets only for a specific reason; summarize before reading more.

If a broad read is necessary, state why and cap it to the smallest useful scope.

## Long-Running Work

Treat phase changes as context checkpoints.

- Before implementation or repo/task switches, preserve the conclusion, next decision, nearest next step, and smallest useful boundary.
- In repos using `project-context`, prefer `BRIEF.md` for compact current state and logs for evidence.
- Start a fresh session only when that surface is enough to continue.

Do not store transcripts, validation matrices, or file inventories to compensate for a large conversation.

## Subagents

Use subagents only when they reduce main-thread noise.

Keep them bounded and usually read-only. Prompt with goal, scope, constraints, expected output, done condition, and validation command if relevant. Ask for findings with evidence, impact boundary, and unknowns; avoid duplicate scopes; close agents after integration.

Use multiple subagents only for independent questions with different scopes.

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

When asked where tokens went, run `scripts/summarize_codex_usage.py --help`, then audit with an explicit `--cwd-prefix`.

The script groups Codex rollout logs by root thread and reports token totals, tool-output size, large-output events, browser/image, DOM/body, broad-search, and top-output-tool signals without raw payloads.

Treat token totals as signals, not quality. Avoid home-wide text searches; point the script at `$CODEX_HOME/sessions` or another explicit sessions root.

## Final Check

- Did the main thread receive only the evidence needed for the current decision?
- Were large reads, browser loops, and subagents bounded by explicit questions?
- Is resumable state in the right surface before a phase shift?
- Did always-read guidance stay short and route detail elsewhere?
