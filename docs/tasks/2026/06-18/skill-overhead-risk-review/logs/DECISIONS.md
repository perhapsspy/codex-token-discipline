# Decisions

**2026-06-18**

- Background: The token-discipline skill is meant to prevent context bloat, but loading the skill and running its script also creates some token output.
- Decision: Treat this as a separate follow-up review task rather than immediately reverting the `776d19c` refresh.
- Why: Current measurements show modest added overhead and plausible net benefit, but the user wants a new session to evaluate the risk from multiple angles before further edits.
- Impact: The next session should start from `BRIEF.md`, use `OVERHEAD-RISK-ASSESSMENT.md` as the current assessment, and only edit runtime surfaces if one mitigation clearly beats leaving the current behavior unchanged.
