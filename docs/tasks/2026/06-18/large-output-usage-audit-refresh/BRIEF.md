# Large Output Usage Audit Refresh

## Goal

- Correct the bundled `codex-token-discipline` usage-audit script so it uses token-event time and cumulative-token deltas, while retaining compact output-control guidance.

## Scope

- Update the shipped skill contract, bundled summarizer, and focused tests.
- Keep the existing CLI compatible; add explicit reproducible-window flags.
- Do not change model or reasoning defaults, installed skill cache, release, or catalog state.

## Current Facts

- Recent audits showed high token sessions were dominated by repeated input context and large dynamic tool outputs, especially command output, browser `js`, `view_image`, body/DOM dumps, screenshots, and continuation/fork reuse.
- The skill already shipped `scripts/summarize_codex_usage.py`; the refresh extends it rather than adding another tool.
- The repo publish/update path is GitHub push followed by `npx skills update codex-token-discipline -g -y`.

## Current State

- Rollout `token_count` records are cumulative snapshots; filesystem mtime cannot identify the requested accounting window.
- `turn_context` records contain the observed model and effort. Missing event time or context must remain unknown.
- Fork files can replay nested ancestor history; the final replay snapshot is a baseline, not child usage.
- A replaying fork becomes attributable only at its first matching child `thread_settings_applied` event; a missing boundary remains unknown.
- The focused suite has 12 passing tests, the bounded exact-window audit completed, and the scoped diff is clean.

## Next Step

- The coordinating parent should commit and push the validated canonical source, then generate and review the bundle integration. Installed cache, release, and catalog state remain outside this task.
