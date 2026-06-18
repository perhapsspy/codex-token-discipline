# Skill Overhead Risk Review

## Goal

- Decide whether `codex-token-discipline` and its bundled usage-audit script should be further trimmed, gated, or documented so they do not create more token cost than they save.

## Scope

- Evaluate the installed skill contract, the `scripts/summarize_codex_usage.py` workflow, and the one-line global AGENTS routing rule.
- Compare the compact pre-refresh state against the current `776d19c` refresh.
- Keep global model/reasoning defaults out of scope; the user explicitly deferred that line of work.

## Current Facts

- The current `SKILL.md` is 4,631 chars / 89 lines / 690 words after compaction.
- Versus the pre-mitigation `776d19c` state, `SKILL.md` is down 325 chars / 3 lines / 58 words.
- The global and portable AGENTS routing line is now 108 chars and no longer says to use the skill "early."
- The script source grew by 2,468 chars, but source text is not loaded when the script runs; the relevant runtime cost is script output.
- Current mitigation-pass script samples range from 802 chars / 9 lines for a narrow repo top-5 audit to 8,205 chars / 53 lines for `<projects-root>` top-15.
- Script output remains acceptable for explicit audits but too large for habitual preflight use.

## Current State

- Current assessment: keep the `776d19c` direction with mitigation. Skill loading and script execution remain conditional tools, not default ceremony.
- Implemented mitigation: compact the English/Korean skill wording and replace the global/portable AGENTS "use early" line with a narrower trigger line.
- Script behavior is intentionally unchanged. The risk is unnecessary skill triggering, repeated audit runs, wide prefixes such as a home directory, or using script output as a gateway into broad raw-log digging.
- Validation passed for script syntax/help, narrow and wider audit runs, project-context shape, and whitespace diffs.
- A detailed restartable assessment and follow-up options are in `OVERHEAD-RISK-ASSESSMENT.md`.

## Next Step

- Publish or reinstall only if the user wants this repo version propagated.

## Working Boundary

- `skills/codex-token-discipline/SKILL.md`
- `skills/codex-token-discipline/SKILL.ko.md`
- `skills/codex-token-discipline/scripts/summarize_codex_usage.py`
- `docs/reference/observed-token-patterns.md`
- external: `$CODEX_HOME/AGENTS.md` and portable `codex/AGENTS.md`
