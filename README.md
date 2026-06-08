# Codex Token Discipline

[한국어](README.md) | [English](README.en.md)

## 요약

`codex-token-discipline`은 긴 Codex 작업에서 컨텍스트가 noisy read, 큰 출력, 반복 브라우저 루프, 넓은 서브에이전트 위임, 비대한 always-read 지침 때문에 커지는 것을 막는 운영 스킬입니다.

최종 답변을 무조건 줄이는 스킬이 아니라, 중간 작업을 summary-first read, bounded delegation, compact resume state, phase-boundary reset으로 관리하게 합니다.

`스펙:` Agent Skills / SKILL.md | `라이선스:` MIT | `에이전트:` Codex, ChatGPT, Agent Skills 호환 도구

## 빠른 시작

**설치**

```bash
npx skills add perhapsspy/codex-token-discipline
```

혹은 `skills/codex-token-discipline` 폴더를 에이전트 스킬 디렉터리에 직접 복사합니다.

**바로 사용**

```text
$codex-token-discipline 을 사용해서 이 긴 Codex 작업을 summary-first read, bounded subagent, compact resume surface 중심으로 진행해줘
```

## 이런 때 사용

- repo를 넓게 탐색하거나 큰 diff/log/test output을 읽기 시작할 때
- 브라우저나 UI 픽셀 디버깅 루프가 길어질 때
- 여러 subagent를 쓰되 main thread를 noisy transcript로 채우고 싶지 않을 때
- 긴 작업의 phase가 바뀌어 `BRIEF.md` 같은 resume surface를 갱신해야 할 때
- AGENTS, skills, MCP, memory 같은 always-read/always-available 표면을 늘리기 전에 비용을 따져야 할 때
- Codex 세션 로그에서 최근 토큰 사용 패턴을 감사하고 싶을 때

## 더 보기

- 스킬 상세 규칙: [English](skills/codex-token-discipline/SKILL.md) | [한국어](skills/codex-token-discipline/SKILL.ko.md)
- 방향 문서: [docs/skill-direction.md](docs/skill-direction.md)
- 관측 패턴: [docs/reference/observed-token-patterns.md](docs/reference/observed-token-patterns.md)

## 지원

[![Buy Me A Coffee](https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png)](https://www.buymeacoffee.com/perhapsspy)

## 라이선스

[MIT](LICENSE)
