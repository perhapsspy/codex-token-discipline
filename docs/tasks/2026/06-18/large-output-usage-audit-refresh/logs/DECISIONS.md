# Decisions

**2026-06-18**

- Background: The skill already referenced a bundled usage summarizer, and repo direction kept deterministic local usage audit as an explicit evolution criterion.
- Decision: Extend the existing summarizer rather than adding another audit tool or removing the Usage Audit section.
- Why: The observed token leaks are recurring structural patterns, and a small script can surface them without making agents reread raw rollout logs.
- Impact: Future usage audits should start with the script and only inspect raw logs after a specific hotspot is isolated.

**2026-06-18**

- Background: Global AGENTS files are always-read, while detailed output-control procedure belongs in the skill.
- Decision: Add only one high-token routing rule to AGENTS and keep detailed guardrails in `codex-token-discipline`.
- Why: This changes future agent behavior without turning startup instructions into a procedure document.
- Impact: Future refinements should prefer skill edits unless the always-read routing rule itself is wrong.
