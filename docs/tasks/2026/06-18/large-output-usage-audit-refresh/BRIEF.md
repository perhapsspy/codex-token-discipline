# Large Output Usage Audit Refresh

## Goal

- Refresh the installed `codex-token-discipline` skill so it directly guides large command/browser/image output control and provides a compact usage-audit script for diagnosing token hotspots.

## Scope

- Update the shipped skill contract in `skills/codex-token-discipline/`.
- Keep `$CODEX_HOME/AGENTS.md` and the portable `codex/AGENTS.md` change to one routing rule.
- Do not change global model or reasoning defaults.

## Current Facts

- Recent audits showed high token sessions were dominated by repeated input context and large dynamic tool outputs, especially command output, browser `js`, `view_image`, body/DOM dumps, screenshots, and continuation/fork reuse.
- The skill already shipped `scripts/summarize_codex_usage.py`; the refresh extends it rather than adding another tool.
- The repo publish/update path is GitHub push followed by `npx skills update codex-token-discipline -g -y`.

## Current State

- The runtime skill now treats large tool results as future input cost and names browser/image/body/DOM outputs as main-thread risk.
- The usage-audit script reports tool-output size, max output size, large-output event counts, browser/image and DOM/body signals, broad absolute-path searches, and top output tools without printing raw payloads.
- Global and portable AGENTS route high-token work to `$codex-token-discipline` early.
- Local validation passes: skill validation in a temporary PyYAML venv, script syntax/help, bounded playground and Conalog sample audits, project-context shape, and diff whitespace checks.

## Next Step

- Commit, push, then refresh the global installed skill with `npx skills update codex-token-discipline -g -y`.
