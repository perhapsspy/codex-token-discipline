# Codex Token Discipline (한국어 페어)

> 영문 기본 문서: `SKILL.md`

## 목적

긴 Codex 작업에서 noisy read, 반복 큰 출력, 넓은 위임, 비대한 always-read 지침이 컨텍스트를 밀어내지 않게 한다. 최종 답변을 줄이는 스킬이 아니다.

## 실행 프레임

행동을 바꾸는 것만 쓴다.

1. 현재 단계를 이름 붙인다: explore, plan, implement, verify, publish, handoff.
2. 넓게 읽기 전에 다음 결정에 필요한 증거를 정한다.
3. 전체 파일, diff, 로그, 스크린샷, 명령 출력보다 요약과 제한된 읽기를 먼저 쓴다.
4. noisy한 보조 작업은 근거 있는 findings를 돌려줄 수 있을 때만 위임한다.
5. 단계가 바뀔 때는 계속하거나 새 세션을 시작하기 전에 compact resume state를 남긴다.

작은 수정, 직접 답변, 단순 명령까지 긴 의식으로 만들지 않는다.

## Summary-First Reads

좁게 시작하고, 다음 결정이 바뀔 때만 넓힌다.

- 파일을 열기 전에 `rg`나 파일 목록을 먼저 쓴다.
- 전체 diff보다 `git diff --stat`, `git diff --name-only`, focused `git diff -- <path>`, 좁은 `sed -n` 범위를 먼저 본다.
- 로그와 명령 출력은 전체 transcript보다 `tail`, `head`, `jq`, count, filter, 에러 검색을 먼저 쓴다.
- 생성/테스트 출력은 주요 실패와 명령만 남기고, 메인 스레드에서 반복 full rerun을 피한다.
- 큰 tool result는 다음 turn의 입력 비용으로 본다. 1만 자 안팎을 넘길 명령은 전체 출력 전에 count, path, summary, 첫 actionable failure를 먼저 요청한다.
- 출력 예산은 구체적 이유가 있을 때만 키우고, 더 읽기 전에 요약한다.

넓은 읽기가 필요하면 이유를 말하고 다음 읽기를 가장 작은 유용한 범위로 제한한다.

## 긴 작업

단계 전환을 컨텍스트 체크포인트로 본다.

- 구현 전이나 repo/task 전환 전에는 결론, 다음 결정, 가장 가까운 다음 단계, 최소 유용 경계를 보존한다.
- `project-context`를 쓰는 repo에서는 compact current state는 `BRIEF.md`, 근거는 logs에 둔다.
- 그 surface만으로 이어갈 수 있을 때만 새 세션을 시작한다.

큰 대화를 보상하려고 transcript, 검증 matrix, 파일 inventory를 저장하지 않는다.

## 서브에이전트

서브에이전트는 main-thread noise를 줄일 때만 쓴다.

bounded, 보통 read-only로 둔다. goal, scope, constraints, expected output, done condition, 필요하면 validation command를 작게 전달한다. raw notes가 아니라 evidence가 있는 findings, impact boundary, unknowns를 요청하고, 중복 범위를 피하며, 통합 뒤 닫는다.

여러 subagent는 서로 독립된 질문과 범위가 있을 때만 쓴다.

## 브라우저와 UI 루프

반복 시각 검증 전에 확인할 상태를 먼저 적는다.

- 상태 하나당 screenshot/browser pass 하나를 기본으로 한다.
- 실패하면 console error, DOM state, route data, focused component처럼 가장 작은 owner를 본다.
- 다음 결정에 영향을 주지 않는 image, base64 screenshot, full body text, DOM dump는 main thread로 들고 오지 않는다.
- 지정한 상태가 검증되거나 구체적 blocker가 분리되면 멈춘다.

## Always-Read Surface

global/repo instruction의 모든 줄은 반복 비용을 가진다.

- AGENTS류 파일에는 durable behavior rule과 safety boundary를 둔다.
- 반복 workflow는 skill에 둔다.
- 현재 task state는 repo task docs에 둔다.
- 현재 재사용 가능한 domain fact는 reference docs에 둔다.
- stale profile, duplicate instruction, historical explanation은 문서로 우회하지 말고 제거한다.

always-read 파일을 고칠 때는 절차보다 짧은 routing rule을 선호한다.

## Usage Audit

사용자가 토큰이 어디에 쓰였는지 물으면 `scripts/summarize_codex_usage.py --help`를 본 뒤 명시적 `--cwd-prefix`로 감사한다.

스크립트는 Codex rollout log를 root thread로 묶어 token total, tool-output size, large-output event, browser/image, DOM/body, broad search, top output tool 신호를 보여준다. raw payload는 출력하지 않는다.

토큰 총량은 품질 기준이 아니라 신호로 본다. 홈 전체 텍스트 검색은 피하고, `$CODEX_HOME/sessions` 같은 명시적 sessions root를 지정한다.

## 최종 확인

- main thread가 현재 결정에 필요한 증거만 받았는가?
- 큰 읽기, browser loop, subagent가 명시적 질문으로 제한됐는가?
- 단계 전환 전에 resumable state가 맞는 surface에 있는가?
- always-read guidance는 짧게 남고 상세는 다른 곳으로 route됐는가?
