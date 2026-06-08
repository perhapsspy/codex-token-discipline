---
name: codex-token-discipline
description: Use when Codex work risks high token use from long sessions, broad repository exploration, large diffs/logs, browser debugging loops, many subagents, or expanding always-read instructions. Keeps context use disciplined through summary-first reads, bounded delegation, compact resume surfaces, and phase-boundary resets; can audit Codex session token usage when asked.
---

# Codex Token Discipline

## Purpose

Keep long Codex work effective without letting context grow from noisy reads, repeated large outputs, broad delegation, or oversized always-read instructions.

This skill is for operating the task, not for making the final answer terse. Preserve the user's requested depth while keeping intermediate context intentional.

## Operating Frame

Use the smallest frame that changes behavior:

1. Name the current phase: explore, plan, implement, verify, publish, or handoff.
2. Define the next evidence needed before reading broadly.
3. Prefer summaries and bounded reads before full files, diffs, logs, screenshots, or command output.
4. Delegate noisy side work only when it can return distilled findings.
5. At phase boundaries, save compact resume state before continuing or starting a fresh session.

Do not turn this into a ritual for small edits, direct answers, or simple commands.

## Summary-First Reads

Start narrow, then widen only when the result changes the next decision.

- Search with `rg` or file lists before opening files.
- Prefer `git diff --stat`, `git diff --name-only`, focused `git diff -- <path>`, and targeted `sed -n` ranges before full diffs.
- For logs and command output, use `tail`, `head`, `jq`, counts, filters, or error-specific searches before full transcripts.
- For generated or test output, keep the first actionable failure and the command that produced it; avoid repeated full reruns in the main thread.
- Raise output budgets only for a specific reason, and summarize what was learned before reading more.

If a broad read is necessary, state why and cap the next read to the smallest useful scope.

## Long-Running Work

Treat phase changes as context checkpoints.

- After exploration, preserve the conclusion and the next decision before implementation.
- Before switching tasks or repos, write or refresh the repo's existing resume surface.
- In repos using `project-context`, prefer `BRIEF.md` for compact current state and logs for evidence.
- Keep resume state current, not historical: goal, scope, current facts, current state, nearest next step, and only the smallest useful file boundary.
- Start a fresh session when the saved resume surface is enough to continue and the remaining work is a new phase.

Do not save command transcripts, validation matrices, or file inventories into the resume surface just to compensate for a large conversation.

## Subagents

Use subagents to reduce main-thread context pollution, not to multiply vague work.

- Make read-heavy subagents bounded and usually read-only.
- Pass a small prompt: goal, scope, constraints, expected output, done condition, and validation command if relevant.
- Ask for findings, evidence, impact boundary, and unknowns rather than raw notes.
- Avoid duplicate agents on the same question.
- Close agents after integrating results.

Use multiple subagents only for independent questions with different scopes.

## Browser And UI Loops

Before repeated visual or browser verification, write down the states to check.

- Prefer one screenshot or browser pass per named state.
- If a check fails, inspect the smallest owner: console error, DOM state, route data, or focused component.
- Keep image and browser artifacts out of the main thread unless they affect the next decision.
- Stop the visual loop once the named states are verified or a concrete blocker is isolated.

## Always-Read Surfaces

Every line in global or repo instructions has recurring cost.

- Put durable behavior rules and safety boundaries in AGENTS-style files.
- Put repeatable workflows in skills.
- Put current task state in repo task docs.
- Put current reusable domain facts in reference docs.
- Remove stale profiles, duplicate instructions, and historical explanations instead of documenting around them.

When editing an always-read file, prefer a short routing rule over a procedure.

## Usage Audit

When the user asks where tokens went, use `scripts/summarize_codex_usage.py` from this skill instead of rewriting an ad hoc parser.

Example:

```bash
python <skill-dir>/scripts/summarize_codex_usage.py \
  --sessions-root ~/.codex/sessions \
  --cwd-prefix /Users/pie/Projects/conalog \
  --since-days 14 \
  --top 15
```

The script reads Codex `rollout-*.jsonl` files, uses the last cumulative `token_count` per session, groups subagents with their root thread, and reports repo totals plus high-token task clusters.

Use the report as a diagnosis aid. Do not treat token totals as the only quality metric; high-token work may be justified when it closes a risky task.

## Final Check

- Did the main thread receive only the evidence needed for the current decision?
- Were large reads, browser loops, and subagents bounded by explicit questions?
- Is resumable state in the right surface before a phase shift?
- Did always-read guidance stay short and route detail elsewhere?
