# BRIEF

## Goal

Create and publish the first `codex-token-discipline` skill as a personal Agent Skills repo, then install it globally for local Codex use.

## Scope

- Build a standalone skill repo following the existing personal skill repo pattern.
- Include a compact runtime skill, Korean companion, README pair, local direction/reference docs, and a small Codex usage-audit script.
- Push the repo to GitHub and install it with `npx skills`.

## Current State

- The skill contract focuses on summary-first reads, bounded subagents, phase-boundary resume state, browser/UI loop limits, always-read surface routing, and optional usage audit.
- Existing public skills were checked; none matched this Codex-specific workflow closely enough to install as-is.
- Local validation passes for skill metadata, project-context runtime shape, Python syntax, and a sample Conalog usage audit.
- The repo is published at `https://github.com/perhapsspy/codex-token-discipline` and globally installed for Codex at `$AGENTS_HOME/skills/codex-token-discipline`.
- A post-release review found only low-risk compaction opportunities in `SKILL.md` and `SKILL.ko.md`; README/docs do not need changes.

## Next Step

Validate the compacted skill text, publish it, and refresh the global skill install.

## Working Boundary

- `skills/codex-token-discipline/`
- `README.md`
- `README.en.md`
- `docs/skill-direction.md`
- `docs/reference/observed-token-patterns.md`
