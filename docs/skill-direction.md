# Skill Direction

## Purpose

`codex-token-discipline` reduces total root-and-child cost from avoidable intermediate work.

It should help agents decide how to choose bounded execution and observation, read, delegate, checkpoint, and audit work while preserving task success, required evidence, and the user's requested outcome.

Keep implicit invocation enabled so prevention can act before costly execution, excess output, or delegation accumulates. Keep the metadata trigger narrow enough to skip routine work.

## Keep

- Summary-first reads before full files, diffs, logs, screenshots, or test transcripts.
- A preflight output contract for unpredictable or batch tool calls: smallest useful return shape, finite budget, and source-side reduction.
- Artifact-plus-summary handling when full output is worth preserving, with bounded follow-up reads from the artifact.
- One bounded named agent by default, with parallel work limited to independent, non-overlapping scopes.
- Compact phase-boundary resume state, especially `BRIEF.md` in repos that use `project-context`, while a coordinating director owns continue, handoff, and session-rotation decisions.
- Clear routing from always-read files to skills and repo docs.
- A deterministic local usage-audit script when the user asks where tokens went.

## Avoid

- Turning the skill into a generic "answer briefly" rule.
- Repeating `project-context`, `agents-md-editor`, or browser hygiene contracts.
- Adding Codex-internal claims that are not observable from current local logs or official docs.
- Making every task run a token ritual.
- Treating cleaner main-thread context as a cost win by itself.
- Waiting for a single large-output threshold or summarizing only after noisy output has already entered the main context.
- Owning session rotation inside the skill when a director coordinates the long-running workflow.
- Keeping large examples in the shipped skill body.

## Evolution

Add rules only when repeated work shows a concrete failure mode: large output loops, stale resume state, duplicated always-read guidance, broad unfocused subagents, or repeated ad hoc token parsers.

Put detailed examples or investigations in repo docs. Keep the shipped skill short enough to load during a real task.
