# Codex Token Discipline (한국어 페어)

> 영문 기본 문서: `SKILL.md`

## 목적

task 성공, 필요한 증거와 요청된 산출물을 약화하지 않으면서 root와 child의 총비용을 줄인다.

read, tool output, retry와 delegation을 제한한다. 재사용 가능한 증거를 보존하고 해소되지 않은 부분만 escalate한다.

## 실행 프레임

행동을 바꾸는 것만 쓴다.

1. 현재 단계를 이름 붙인다: explore, plan, implement, verify, publish, handoff.
2. 넓게 읽기 전에 다음 결정에 필요한 증거를 정한다.
3. noisy할 수 있는 tool call 전에 가장 작은 유용한 반환 형태와 출력 예산을 정한다.
4. noisy한 보조 작업은 근거 있는 findings를 돌려줄 수 있을 때만 위임한다.
5. 단계가 바뀔 때는 compact resume state를 남기고, director가 있으면 세션 지속 여부 결정을 director에게 넘긴다.

작은 수정, 직접 답변, 단순 명령까지 긴 의식으로 만들지 않는다.

## 실행 전 출력 계약

과도한 출력이 main context에 들어오기 전에 막는다. 들어온 뒤 요약하는 방식에 의존하지 않는다.

- 예측하기 어렵거나 batch 성격인 명령은 status, count, path, 선택 필드, 첫 actionable failure 중 필요한 반환 형태를 먼저 정한다.
- tool call에 유한한 반환 예산을 둔다. exec 계열은 특정 근거가 더 필요하지 않으면 명시적 2,000-token 이하를 기본으로 한다. 단일 large-output 임계값을 넘을 때까지 기다리지 않는다.
- source에서 filter, aggregate, select한다. test/build는 더 자세히 보기 전에 exit status, 첫 actionable failure, command를 반환한다.
- 전체 출력이 나중 점검에 유용하면 task-local 또는 임시 artifact에 쓰고, main context에는 path, size, compact summary, 첫 actionable failure만 반환한다. 이후에는 artifact의 제한된 범위만 본다.
- source에서 줄일 수 있는 일회성 출력에는 artifact를 만들지 않는다.

## Summary-First Reads

좁게 시작하고, 다음 결정이 바뀔 때만 넓힌다.

- 파일을 열기 전에 `rg`나 파일 목록을 먼저 쓴다.
- 전체 diff보다 `git diff --stat`, `git diff --name-only`, focused `git diff -- <path>`, 좁은 `sed -n` 범위를 먼저 본다.
- 로그와 명령 출력은 전체 transcript보다 `tail`, `head`, `jq`, count, filter, 에러 검색을 먼저 쓴다.
- 반환된 모든 tool result는 다음 turn의 입력 비용으로 본다. 전체 출력보다 count, path, summary, 선택된 근거를 먼저 요청한다.
- 실패 뒤에는 저장된 artifact에서 범위를 넓히거나 가장 작은 실패 범위만 다시 실행한다. main thread에 full transcript를 반복해서 들이지 않는다.

넓은 읽기가 필요하면 이유를 말하고 다음 읽기를 가장 작은 유용한 범위로 제한한다.

## 긴 작업

단계 전환을 컨텍스트 체크포인트로 본다.

- 구현 전이나 repo/task 전환 전에는 결론, 다음 결정, 가장 가까운 다음 단계, 최소 유용 경계를 보존한다.
- `project-context`를 쓰는 repo에서는 compact current state는 `BRIEF.md`, 근거는 logs에 둔다.
- director가 긴 작업을 조율하면 checkpoint를 보고하고, 계속할지 handoff/rotation할지는 director가 결정하게 한다. 새 세션을 무조건 권고하거나 직접 시작하지 않는다.
- director가 없으면 저장된 surface만으로 이어갈 수 있고 사용자나 owning workflow가 요구할 때만 새로 시작한다.

큰 대화를 보상하려고 transcript, 검증 matrix, 파일 inventory를 저장하지 않는다.

## 서브에이전트

위임 자체가 더 저렴한 것은 아니다. compact하고 독립적으로 유용한 증거나 산출물을 돌려줄 수 있는 bounded 작업에는 가장 좁은 named agent를 쓴다.

agent 하나로 시작한다. 서로 독립되고 겹치지 않는 범위만 병렬화한다. 같은 조사를 중복하거나 통합 뒤 agent를 유지하거나 아직 유효한 검증을 반복하지 않는다.

scope, write boundary, done condition, validation과 기대하는 compact output을 전달한다. child는 다시 위임하지 않는다.

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

사용자가 토큰이 어디에 쓰였는지 물으면 이 스킬이 설치된 디렉터리를 기준으로 `scripts/summarize_codex_usage.py` 경로를 찾고 `--help`를 본 뒤, 명시적 `--cwd-prefix`로 감사한다.

스크립트는 Codex rollout log를 root thread로 묶어 token total, cached-input rate, child-session token share, tool-output volume, large-output event, top output tool 신호를 보여준다. raw payload는 출력하지 않는다.

토큰 총량은 품질 기준이 아니라 신호로 본다. 홈 전체 텍스트 검색은 피하고, `$CODEX_HOME/sessions` 같은 명시적 sessions root를 지정한다.

## 최종 확인

- main thread가 현재 결정에 필요한 증거만 받았는가?
- noisy tool 작업에 실행 전 반환 형태와 예산이 있었고, 전체 상세는 유용할 때만 artifact에 남겼는가?
- 큰 읽기, browser loop, subagent가 명시적 질문으로 제한됐는가?
- resumable state가 맞는 surface에 있고 continue/handoff/rotation 결정은 owning director에게 남았는가?
- always-read guidance는 짧게 남고 상세는 다른 곳으로 route됐는가?
