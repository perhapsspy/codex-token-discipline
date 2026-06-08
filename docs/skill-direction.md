# Skill Direction

## Purpose

`codex-token-discipline` keeps Codex work from spending context on avoidable intermediate noise.

It should help agents decide how to read, delegate, checkpoint, and audit work while preserving the user's requested outcome.

## Keep

- Summary-first reads before full files, diffs, logs, screenshots, or test transcripts.
- Bounded read-only subagents for noisy exploration.
- Compact phase-boundary resume state, especially `BRIEF.md` in repos that use `project-context`.
- Clear routing from always-read files to skills and repo docs.
- A deterministic local usage-audit script when the user asks where tokens went.

## Avoid

- Turning the skill into a generic "answer briefly" rule.
- Repeating `project-context`, `agents-md-editor`, or browser hygiene contracts.
- Adding Codex-internal claims that are not observable from current local logs or official docs.
- Making every task run a token ritual.
- Keeping large examples in the shipped skill body.

## Evolution

Add rules only when repeated work shows a concrete failure mode: large output loops, stale resume state, duplicated always-read guidance, broad unfocused subagents, or repeated ad hoc token parsers.

Put detailed examples or investigations in repo docs. Keep the shipped skill short enough to load during a real task.
