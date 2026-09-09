# Worklog

**2026-09-09**

- Reworked the bundled usage summarizer to aggregate deltas at `token_count` event times instead of filtering files by mtime or taking one final cumulative total.
- Added explicit `--since` and `--until` bounds, observed model/effort attribution, root/child input-cached-output reporting, timestamp-filtered tool metrics, reset handling, and nested-fork replay baselines.
- Added synthetic regressions for repeated cumulative records, reset records, turn-context model changes, and nested fork replay; missing event timestamps and model context remain explicitly unknown.
- Corrected the replay boundary after an independent review: suppress inherited events through the first child `thread_settings_applied` marker, then use the next pre-task snapshot as the child baseline. Markerless replay stays unknown.
- Validated the final source with all 12 focused tests, a bounded exact-window audit, project-context shape, and a clean whitespace diff.

**2026-06-18**

- Reviewed the existing global and portable AGENTS content, the skill repo ownership rules, shipped English/Korean skill pair, direction/reference docs, and existing usage-audit script.
- Used bounded support agents: one mapped the repo's `npx skills` publish/update flow and document ownership, and one assessed whether the summarizer should remain a bundled script.
- Added one concise high-token routing rule to `$CODEX_HOME/AGENTS.md` and the portable `codex/AGENTS.md`; global reasoning defaults were intentionally left unchanged.
- Updated `SKILL.md` and `SKILL.ko.md` to call out large tool-result input cost, browser/image/body/DOM main-thread risk, and explicit sessions-root usage during audits.
- Extended `scripts/summarize_codex_usage.py` to report output size metrics, large-output buckets, browser/image and DOM/body signals, broad absolute-path searches, fork parent grouping, and top output tools without exposing raw payloads.
- Validated with `py_compile`, script `--help`, bounded playground and Conalog sample audits, project-context runtime shape, diff whitespace, and skill-creator quick validation in a temporary PyYAML venv.
