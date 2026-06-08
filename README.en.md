# Codex Token Discipline

[한국어](README.md) | [English](README.en.md)

## Summary

`codex-token-discipline` helps long Codex work avoid context growth from noisy reads, large outputs, repeated browser loops, broad subagent delegation, and oversized always-read instructions.

It does not force terse final answers. It keeps intermediate work disciplined through summary-first reads, bounded delegation, compact resume state, and phase-boundary resets.

`Spec:` Agent Skills / SKILL.md | `License:` MIT | `Agents:` Codex, ChatGPT, and Agent Skills-compatible tools

## Quick Start

**Install**

```bash
npx skills add perhapsspy/codex-token-discipline
```

Or copy `skills/codex-token-discipline` directly into an agent skill directory.

**Use**

```text
Use $codex-token-discipline to keep this long Codex task efficient with summary-first reads, bounded subagents, and a compact resume surface.
```

## Use When

- Broad repository exploration, large diffs, logs, or test output are about to enter the thread.
- Browser or UI pixel debugging loops are growing.
- Subagents should help without returning raw transcript noise to the main thread.
- A long task crosses a phase boundary and needs a refreshed resume surface such as `BRIEF.md`.
- Always-read or always-available surfaces such as AGENTS files, skills, MCP, or memory are expanding.
- You want to audit recent Codex session token usage from local rollout logs.

## More

- Skill rules: [English](skills/codex-token-discipline/SKILL.md) | [한국어](skills/codex-token-discipline/SKILL.ko.md)
- Direction: [docs/skill-direction.md](docs/skill-direction.md)
- Observed patterns: [docs/reference/observed-token-patterns.md](docs/reference/observed-token-patterns.md)

## Support

[![Buy Me A Coffee](https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png)](https://www.buymeacoffee.com/perhapsspy)

## License

[MIT](LICENSE)
