# Skill Overhead Risk Review

## Goal

- Decide whether `codex-token-discipline` and its bundled usage-audit script should be further trimmed, gated, or documented so they do not create more token cost than they save.

## Scope

- Evaluate the installed skill contract, the `scripts/summarize_codex_usage.py` workflow, and the one-line global AGENTS routing rule.
- Compare the compact pre-refresh state against the current `776d19c` refresh.
- Keep global model/reasoning defaults out of scope; the user explicitly deferred that line of work.

## Current Facts

- The current installed `SKILL.md` is 4,956 chars / 92 lines / 748 words.
- The `776d19c` refresh added 488 chars / 3 lines / 71 words to `SKILL.md` versus `61c6a7c`.
- The global AGENTS routing line adds 119 chars of always-read startup cost.
- The script source grew by 2,468 chars, but source text is not loaded when the script runs; the relevant runtime cost is script output.
- Same-input script output increased from 527 to 776 chars for the playground sample and from 2,582 to 3,925 chars for the Conalog top-5 sample.
- Current default Conalog top-15 script output is about 7,923 chars; this is small relative to the 40k-1M+ raw outputs the script is meant to avoid, but too large for habitual preflight use on every task.

## Current State

- Current assessment: keep the `776d19c` direction for now, but treat both skill loading and script execution as conditional tools, not default ceremony.
- The risk is not the script source size; the risk is unnecessary skill triggering, repeated audit runs, wide prefixes such as a home directory, or using script output as a gateway into broad raw-log digging.
- A detailed restartable assessment and follow-up options are in `OVERHEAD-RISK-ASSESSMENT.md`.

## Next Step

- Review `OVERHEAD-RISK-ASSESSMENT.md` and decide whether to implement one of the proposed mitigations: tighten the AGENTS routing phrase, reduce the script default `--top`, add a quiet/summary mode, or leave current behavior unchanged.

## Working Boundary

- `skills/codex-token-discipline/SKILL.md`
- `skills/codex-token-discipline/SKILL.ko.md`
- `skills/codex-token-discipline/scripts/summarize_codex_usage.py`
- `docs/reference/observed-token-patterns.md`
- external: `$CODEX_HOME/AGENTS.md` and portable `codex/AGENTS.md`
