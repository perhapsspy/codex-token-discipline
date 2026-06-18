# Decisions

**2026-06-18**

- Background: The token-discipline skill is meant to prevent context bloat, but loading the skill and running its script also creates some token output.
- Decision: Treat this as a separate follow-up review task rather than immediately reverting the `776d19c` refresh.
- Why: Current measurements show modest added overhead and plausible net benefit, but the user wants a new session to evaluate the risk from multiple angles before further edits.
- Impact: The next session should start from `BRIEF.md`, use `OVERHEAD-RISK-ASSESSMENT.md` as the current assessment, and only edit runtime surfaces if one mitigation clearly beats leaving the current behavior unchanged.

**2026-06-18**
- Background: The user wanted both direct skill-text compaction and a narrower routing phrase, while judging script cost by stdout rather than source length.
- Decision: Compact the English and Korean skill contracts, replace the global and portable AGENTS routing line, and leave script behavior unchanged for now.
- Why: AGENTS and selected-skill text are recurring context surfaces, while measured script stdout remains acceptable for explicit audits and changing defaults or adding compact mode would add complexity before evidence requires it.
- Impact: Future work should revisit script defaults only if explicit audit output becomes noisy; prefer lowering --top before adding a new compact mode.
