# Codex Token Discipline (한국어 페어)

> 영문 기본 문서: `SKILL.md`

## 목적

긴 Codex 작업에서 noisy read, 반복되는 큰 출력, 넓은 위임, 비대한 always-read 지침 때문에 컨텍스트가 커지는 것을 막는다.

이 스킬은 최종 답변을 무조건 짧게 만드는 스킬이 아니다. 사용자가 요청한 깊이는 유지하되, 중간 작업 컨텍스트를 의도적으로 관리한다.

## 실행 프레임

행동을 바꾸는 최소 프레임만 쓴다.

1. 현재 단계를 이름 붙인다: explore, plan, implement, verify, publish, handoff.
2. 넓게 읽기 전에 다음 결정에 필요한 증거를 정한다.
3. 전체 파일, diff, 로그, 스크린샷, 명령 출력보다 요약과 제한된 읽기를 먼저 쓴다.
4. noisy한 보조 작업은 요약된 findings를 돌려줄 수 있을 때만 위임한다.
5. 단계가 바뀔 때는 계속하거나 새 세션을 시작하기 전에 compact resume state를 남긴다.

작은 수정, 직접 답변, 단순 명령까지 긴 의식으로 만들지 않는다.

## Summary-First Reads

좁게 시작하고, 다음 결정이 바뀔 때만 넓힌다.

- 파일을 열기 전에 `rg`나 파일 목록을 먼저 쓴다.
- 전체 diff보다 `git diff --stat`, `git diff --name-only`, focused `git diff -- <path>`, 좁은 `sed -n` 범위를 먼저 본다.
- 로그와 명령 출력은 전체 transcript보다 `tail`, `head`, `jq`, count, filter, 에러 전용 검색을 먼저 쓴다.
- 생성/테스트 출력은 주요 실패와 그 명령만 남기고, 메인 스레드에서 반복 full rerun을 피한다.
- 출력 예산은 구체적 이유가 있을 때만 키우고, 더 읽기 전에 배운 점을 요약한다.

넓은 읽기가 필요하면 이유를 말하고 다음 읽기를 가장 작은 유용한 범위로 제한한다.

## 긴 작업

단계 전환을 컨텍스트 체크포인트로 본다.

- 탐색 후에는 구현 전에 결론과 다음 결정을 보존한다.
- 작업이나 repo를 바꾸기 전에 해당 repo의 기존 resume surface를 쓰거나 갱신한다.
- `project-context`를 쓰는 repo에서는 compact current state는 `BRIEF.md`, 근거는 logs에 둔다.
- resume state는 역사 기록이 아니라 현재 상태여야 한다: 목표, 범위, 현재 사실, 현재 상태, 가장 가까운 다음 단계, 최소 파일 경계.
- 저장된 resume surface만으로 이어갈 수 있고 남은 일이 새 단계라면 새 세션을 고려한다.

큰 대화를 보상하려고 command transcript, 검증 matrix, 파일 inventory를 resume surface에 넣지 않는다.

## 서브에이전트

서브에이전트는 main-thread context pollution을 줄이기 위해 쓴다.

- read-heavy subagent는 bounded, 보통 read-only로 둔다.
- goal, scope, constraints, expected output, done condition, 필요하면 validation command를 작게 전달한다.
- raw notes가 아니라 findings, evidence, impact boundary, unknowns를 요청한다.
- 같은 질문을 중복 위임하지 않는다.
- 결과를 통합한 뒤 agent를 닫는다.

여러 subagent는 서로 독립된 질문과 범위가 있을 때만 쓴다.

## 브라우저와 UI 루프

반복 시각 검증 전에 확인할 상태를 먼저 적는다.

- 상태 하나당 screenshot/browser pass 하나를 기본으로 한다.
- 실패하면 console error, DOM state, route data, focused component처럼 가장 작은 owner를 본다.
- 다음 결정에 영향을 주지 않는 이미지와 브라우저 산출물은 main thread로 들고 오지 않는다.
- 지정한 상태가 검증되거나 구체적 blocker가 분리되면 visual loop를 멈춘다.

## Always-Read Surface

global/repo instruction의 모든 줄은 반복 비용을 가진다.

- AGENTS류 파일에는 durable behavior rule과 safety boundary를 둔다.
- 반복 workflow는 skill에 둔다.
- 현재 task state는 repo task docs에 둔다.
- 현재 재사용 가능한 domain fact는 reference docs에 둔다.
- stale profile, duplicate instruction, historical explanation은 문서로 우회하지 말고 제거한다.

always-read 파일을 고칠 때는 절차보다 짧은 routing rule을 선호한다.

## Usage Audit

사용자가 토큰이 어디에 쓰였는지 물으면 ad hoc parser를 다시 만들지 말고 이 스킬의 `scripts/summarize_codex_usage.py`를 쓴다.

예:

```bash
python <skill-dir>/scripts/summarize_codex_usage.py \
  --sessions-root ~/.codex/sessions \
  --cwd-prefix /Users/pie/Projects/conalog \
  --since-days 14 \
  --top 15
```

스크립트는 Codex `rollout-*.jsonl` 파일에서 세션별 마지막 누적 `token_count`를 사용하고, subagent를 root thread로 묶어 repo totals와 high-token task cluster를 보고한다.

토큰 총량은 진단 보조 수단이다. 위험한 작업을 실제로 닫았다면 높은 토큰 사용이 정당할 수 있다.

## 최종 확인

- main thread가 현재 결정에 필요한 증거만 받았는가?
- 큰 읽기, browser loop, subagent가 명시적 질문으로 제한됐는가?
- 단계 전환 전에 resumable state가 맞는 surface에 있는가?
- always-read guidance는 짧게 남고 상세는 다른 곳으로 route됐는가?
