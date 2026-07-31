# Decisions

**2026-07-24**

- **Background:** Recent usage audits show repeated exec-family output is a major context-cost signal, while the existing skill reacts mainly around a roughly 10k-character large-output heuristic.
- **Decision:** Require a preflight return shape and finite output budget for unpredictable or batch calls, and use artifact-plus-summary only when full output is worth preserving.
- **Why:** This changes the call before output reaches the main context and covers repeated moderate outputs that a single-event threshold misses.
- **Impact:** Agents should return status, counts, selected fields, or the first actionable failure by default and widen from a saved artifact only when the next decision needs it.

**2026-07-24**

- **Background:** Long-running phase changes and new-session decisions will be coordinated by a director session.
- **Decision:** Keep compact phase checkpoints in the skill but assign continue, handoff, and rotation decisions to the coordinating director when one exists.
- **Why:** The skill should prepare resumable state without competing with workflow ownership.
- **Impact:** The skill no longer unconditionally recommends or initiates a fresh session.

**2026-07-24**

- **Background:** The summarizer reports total output characters by tool but cannot expose the roughly 8,000-character result average observed in the recent audit.
- **Decision:** Add output-result counts and overall/tool-level average characters while preserving existing totals, buckets, and raw-payload exclusion.
- **Why:** Follow-up audits need a denominator to distinguish repeated moderate output from a few extreme results and verify whether the preflight contract changes behavior.
- **Impact:** Audits can compare output volume per result without broad raw-log inspection.
