# Codex Token Discipline

[한국어](README.md) | [English](README.en.md)

## 요약

긴 작업의 root와 child가 큰 로그, 반복 읽기와 불필요한 위임에 비용을 쓰는 일을 줄입니다. 필요한 증거만 좁게 읽고 재사용하며, 작업 단계가 바뀔 때 현재 상태를 짧게 남깁니다.

## 빠른 시작

**설치**

```bash
npx skills add perhapsspy/codex-token-discipline
```

혹은 `skills/codex-token-discipline` 폴더를 에이전트 스킬 디렉터리에 직접 복사합니다.

**바로 사용**

```text
$codex-token-discipline 이 긴 작업에서 필요한 파일과 로그만 좁게 읽고 다음 단계에 필요한 상태를 짧게 남겨줘.
```

## 이런 때 사용

- repo를 넓게 탐색하거나 큰 diff/log/test output을 읽기 시작할 때
- 출력이 작아도 실행·재시도 비용이 커서 이전 결과로 다음 실행이나 진행 관측을 선택해야 할 때
- 브라우저나 UI 픽셀 디버깅 루프가 길어질 때
- subagent의 총비용과 중복 작업을 제한해야 할 때
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
