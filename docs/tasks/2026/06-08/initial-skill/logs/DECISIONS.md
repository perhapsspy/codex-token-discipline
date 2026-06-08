# Decisions

**2026-06-08**

- Background: The user wanted a reusable response to recent high token use in Conalog Codex work.
- Decision: Create a standalone `codex-token-discipline` repo instead of adding this as a companion skill under `project-context` or `structure-first`.
- Why: The behavior spans reading, delegation, browser loops, always-read surfaces, and session usage audits; no existing sibling skill owns that whole operating concern.
- Impact: The shipped skill can stay independent while routing resume-state behavior to `project-context` when a repo already uses it.
