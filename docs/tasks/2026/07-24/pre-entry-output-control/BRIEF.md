# Pre-Entry Output Control

## Goal

- Make `codex-token-discipline` prevent noisy command and tool output before it enters the main context, while fitting director-owned handoff and session rotation.

## Scope

- Update the shipped English/Korean skill contract and current direction/reference docs.
- Keep agent parallelism policy and generated plugin bundles out of scope.

## Current Understanding

- Recent audits show repeated tool output, especially exec-family output, is a major input-cost signal even when average output per call is below the former large-output heuristic.
- The smallest behavioral change is a preflight return-shape and budget contract, with artifact-plus-summary handling when full output must be preserved.
- The usage summarizer diagnoses output volume but needs output-result counts and averages to measure repeated moderate exec-family output directly.

## Current State

- The source skill now makes a 2,000-token-or-lower exec return budget and pre-entry output control the default for unpredictable or batch calls, and leaves session continuation, handoff, and rotation to the coordinating director.
- The summarizer now reports output-result counts and overall/tool-level average characters without printing raw payloads; focused regression tests cover result counting, unknown tools, averages, the existing 50k bucket, and large `exec` pragma budgets.
- Source validation passes for skill structure, Python syntax, three focused unit tests, bounded real-session audit output, bilingual contract checks, project-context shape, and whitespace.
- A fresh-agent forward test kept an 80,034-byte failing command transcript out of the main result with a 300-token budget and returned the exit status, first actionable failure, artifact path, and size.
- Plugin sync and publication remain out of scope until the source change is committed and pushed.

## Next Step

- Reopen after a comparable 7-day audit if exec output per result or large-output rate does not improve, or if the 2,000-token default hides actionable failure context.

## Working Boundary

- `skills/codex-token-discipline/SKILL.md`
- `skills/codex-token-discipline/SKILL.ko.md`
- `skills/codex-token-discipline/scripts/summarize_codex_usage.py`
- `tests/test_summarize_codex_usage.py`
- `docs/skill-direction.md`
