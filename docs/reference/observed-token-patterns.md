# Token-Usage Diagnostic Signals

## Scope

These are diagnostic heuristics, not claims about every session or project. Confirm them against the session logs and working scope being audited.

## Signals to Check

- Repeated large command outputs, broad file reads, and full diffs can dominate uncached input.
- Browser body text, DOM dumps, images, and encoded screenshots can make a single interaction unusually large.
- Long sessions may accumulate substantial cached input even when each new read is small.
- Broad or duplicate delegation can multiply total usage across agents.
- Reopening work without a compact handoff can repeat discovery and reading costs.
- Large always-read instruction files add recurring overhead to every applicable task.

## How to Use Them

- Start with a summary command and widen only when the next decision needs more evidence.
- Compare phases and tool categories before attributing usage to one event.
- Treat phase changes as a natural point to leave compact resume state.
- Ask delegated agents for bounded findings rather than raw notes.
- Route detailed procedures from always-read files to skills or repository documentation.
- Use the bundled summarizer or an explicitly scoped session-log scan; avoid broad home-directory searches.
- Treat token usage as a diagnostic input, not a standalone quality metric.
