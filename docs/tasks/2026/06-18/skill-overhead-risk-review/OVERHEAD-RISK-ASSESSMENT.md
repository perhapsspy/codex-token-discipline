# Overhead Risk Assessment

## Question

Could `codex-token-discipline` itself, or the bundled `summarize_codex_usage.py` script, increase token use enough to undermine the intended savings?

## Short Answer

Yes, if used as a ritual. No, if used only for high-token work, broad exploration, browser/UI loops, multi-agent work, long session transitions, or explicit token audits.

The current `776d19c` refresh is proportionate: it adds a small amount of skill text and modestly larger audit output in exchange for surfacing the exact high-cost patterns seen in recent sessions. It should not become a default preflight step for ordinary edits.

## Current Measurements

Measured against `61c6a7c` (`Record compact skill refresh`) and current `776d19c` (`Tighten large-output token discipline`):

- `SKILL.md`: 4,468 -> 4,956 chars, 89 -> 92 lines, 677 -> 748 words.
- `SKILL.md` delta: +488 chars, +3 lines, +71 words.
- `SKILL.ko.md`: 2,622 -> 2,963 chars, 86 -> 89 lines, 513 -> 571 words.
- `scripts/summarize_codex_usage.py`: 9,101 -> 11,569 chars, 256 -> 291 lines.
- Script source delta: +2,468 chars, +35 lines, +147 words.
- Global AGENTS routing line: 119 chars.

Same-input script-output comparison:

- Playground sample, `--since-days 3 --top 3`: 527 -> 776 stdout chars.
- Conalog sample, `--since-days 3 --top 5`: 2,582 -> 3,925 stdout chars.
- Current Conalog default top-15 output: about 7,923 stdout chars / 50 lines.
- Current `<projects-root>` default top-15 output: about 7,472 stdout chars / 49 lines.
- Current home-prefix one-day top-5 output: about 2,835 stdout chars / 21 lines.

## Why The Current Direction Can Still Be Net Positive

- The observed expensive failures were much larger than the script output: recent sessions had many 40k+ tool outputs, several 100k+ outputs, and at least one 1M+ image/base64 output.
- The current script does not print raw payloads. It reports counters: token totals, output chars, max output size, large-output counts, browser/image and DOM/body signals, broad absolute-path search counts, and top output tools.
- Those counters identify whether the next fix should target shell output, browser capture, DOM/body dumps, subagent fan-out, or session-boundary behavior.
- The new skill text names the failure modes directly, so future sessions can avoid repeating ad hoc reasoning before acting.

## Ways It Can Become Net Negative

- Triggering the skill for small edits, direct answers, or one-command tasks. Loading about 5k chars of skill text is not worth it there.
- Running the script as a habitual preflight on every task. It is an audit tool, not a normal startup check.
- Using broad prefixes such as a home directory when a repo or workspace prefix would answer the question.
- Running the script repeatedly after every small change instead of once at the start or end of a token investigation.
- Treating script output as a prompt to inspect raw rollout logs broadly. The intended flow is script first, then only narrow raw-log reads for a specific hotspot.
- Adding more cases to `SKILL.md` every time a token issue appears. That would turn the skill into the kind of bulky instruction surface it is meant to prevent.

## Mitigation Options

### Option A: Leave Current Behavior

Keep the current `776d19c` state. This is reasonable if the team follows the current conditional usage rule.

Use when:

- Agents are already respecting "do not turn this into a ritual."
- The script is used only for explicit token audits.
- The extra script fields are proving useful.

Risk:

- The AGENTS phrase "use early" could be over-applied by future agents.

### Option B: Tighten The AGENTS Routing Phrase

Change the global and portable AGENTS line from:

```md
- For high-token work, use `$codex-token-discipline` early to bound large command, browser, image, and subagent output.
```

to something more conditional:

```md
- For broad reads, browser loops, multi-agent work, or token audits, use `$codex-token-discipline` to bound large outputs.
```

Use when:

- Future sessions start loading the skill for ordinary tasks.
- The word "early" appears to cause preflight ceremony.

Risk:

- Slightly weaker prompt to use the skill before a costly loop starts.

### Option C: Reduce Script Default Output

Change `--top` default from 15 to 8 or 10.

Use when:

- Default top-15 output is consistently too long.
- Most audits only need the first few clusters.

Risk:

- Some medium-sized repeated clusters become less visible unless the caller opts into a larger `--top`.

### Option D: Add A Compact Mode

Add `--summary-only` or `--compact` to print repo totals plus top 3 clusters without per-cluster `output_by_tool`.

Use when:

- Agents need a cheap first pass before deciding whether to inspect full script output.

Risk:

- Adds script complexity and another option to remember.

### Option E: Add A Guardrail Warning For Wide Prefixes

Warn when `--cwd-prefix` is a home directory or too short, unless the user passes `--allow-wide-prefix`.

Use when:

- Wide-prefix audits happen accidentally.

Risk:

- Adds friction for legitimate whole-workspace audits.

## Recommended Next Decision

Start with Option A unless real follow-up sessions show over-triggering. If a change is needed, Option B is the smallest behavioral correction because it reduces always-read ambiguity without changing script behavior.

If script output itself becomes the concern, prefer Option C before Option D. Lowering default `--top` is simpler than introducing a new mode.

## Validation For Any Follow-Up Change

- Compare `SKILL.md` char/word count before and after.
- Run `scripts/summarize_codex_usage.py --help`.
- Run one bounded small sample, such as `--cwd-prefix <projects-root>/playground --since-days 3 --top 3`.
- Run one bounded larger sample, such as `--cwd-prefix <projects-root>/conalog --since-days 3 --top 5`.
- Confirm no raw payload, image data, DOM/body text, or long command transcript appears in script output.
- Run project-context shape check and diff whitespace check before publishing.
