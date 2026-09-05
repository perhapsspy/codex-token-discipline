# Codex Token Discipline

[한국어](README.md) | [English](README.en.md)

## Summary

`codex-token-discipline` reduces root-and-child cost from large logs, repeated reads, and unnecessary delegation. It narrows and reuses evidence and leaves compact state when work changes phase.

## Quick Start

**Install**

```bash
npx skills add perhapsspy/codex-token-discipline
```

Or copy `skills/codex-token-discipline` directly into an agent skill directory.

**Use**

```text
Use $codex-token-discipline to read only the files and logs this long task needs and leave a compact state for the next phase.
```

## Use When

- Broad repository exploration, large diffs, logs, or test output are about to enter the thread.
- Execution or retry loops are costly even with small output, and prior results should guide the next execution or progress observation.
- Browser or UI pixel debugging loops are growing.
- Subagent cost and duplicated work need explicit bounds.
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
