# Token-Usage Diagnostic Signals

## Scope

These are diagnostic heuristics, not claims about every session or project. Confirm them against the session logs and working scope being audited.

The `<projects-root>` audit ending 2026-07-24 is the current baseline: about 1.008 billion uncached input tokens, 794 million tool-output characters, and 412 large-output events over 30 days; about 519 million, 142 million, and 166 respectively over 7 days. The 7-day tool-output average was about 8,000 characters per result, with exec-family output as the main signal.

## Signals to Check

- Repeated large command outputs, broad file reads, and full diffs can dominate uncached input.
- Moderate per-call output can still become the dominant cost when repeated often, so prevention should not depend on one large-event threshold.
- Browser body text, DOM dumps, images, and encoded screenshots can make a single interaction unusually large.
- Long sessions may accumulate substantial cached input even when each new read is small.
- Broad or duplicate delegation can multiply total usage across agents.
- Reopening work without a compact handoff can repeat discovery and reading costs.
- Large always-read instruction files add recurring overhead to every applicable task.

## How to Use Them

- Start with a summary command and widen only when the next decision needs more evidence.
- Define the return shape and output budget before unpredictable or batch tool calls; preserve full output as an artifact only when later inspection is useful.
- Compare phases and tool categories before attributing usage to one event.
- Treat phase changes as a natural point to leave compact resume state, then let the coordinating director decide whether to continue, hand off, or rotate.
- Ask delegated agents for bounded findings rather than raw notes.
- Route detailed procedures from always-read files to skills or repository documentation.
- Use the bundled summarizer or an explicitly scoped session-log scan; avoid broad home-directory searches.
- Treat token usage as a diagnostic input, not a standalone quality metric.
