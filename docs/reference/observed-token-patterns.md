# Observed Token Patterns

## Current Facts

- Recent high-token Conalog work was dominated by cached input tokens from long sessions, not only by newly read text.
- The main uncached drivers were repeated large command outputs, broad `sed`/`rg`/`git diff` reads, browser/UI debug loops, and many subagent branches.
- Browser `js`, `view_image`, full body text, DOM dumps, and base64 screenshot emissions can dominate a single turn even when prompt caching is working.
- Subagents can reduce main-thread noise, but broad or duplicate delegation multiplies total token use.
- `BRIEF.md`-style compact resume state lowers reopen cost when long work crosses a phase boundary.
- Always-read files are recurring overhead, so they should route to skills or repo docs instead of carrying detailed procedures.

## Useful Heuristics

- Start with a summary command and only widen when the next decision needs it.
- Treat phase changes as the natural moment to compress current state.
- Ask subagents for findings and boundaries, not raw notes.
- Keep global and repo instructions short enough to scan before acting.
- Use session-log audits for diagnosis, not as a standalone quality metric.
- During audits, use the bundled summarizer or explicit sessions-root scans; avoid broad home-directory text searches over archived rollout logs.
