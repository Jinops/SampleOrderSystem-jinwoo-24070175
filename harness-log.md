# Harness / Plan 검증 로그

`harness-verify`, `plan-verify` Skill을 실행할 때마다 그 결과를 이 파일 맨 아래에 이어서 기록한다. 기존 기록은 수정/삭제하지 않고 새 기록을 추가만 한다.

각 기록은 아래 형식을 따른다.

```
## YYYY-MM-DD HH:MM — 검증 대상 (예: Phase 0~4)

### harness-verify
- 정합성 검사: PASS/FAIL (요약)
- 테스트: PASS/FAIL (요약)

### plan-verify
- 전체 판정: PASS/FAIL (요약)
```

## 2026-07-15 — Phase 0~4

> 묶어서 실행한 사유: `harness-verify`/`plan-verify` Skill 자체가 Phase 4 구현이 끝난 뒤에야 만들어졌기 때문에, Skill이 존재하지 않았던 Phase 0~4는 완성 시점에 한 번에 모아서 검증함.

### harness-verify
- 정합성 검사: PASS
  - 주문 상태 5종/전이 규칙, Sample/Order 필드, 수율 검증 범위(0 초과 1 이하), 승인 시 재고 충분/부족 분기, 모니터링 집계(REJECTED 제외)·재고 분류(여유/부족/고갈) 모두 prd.md/spec.md와 일치.
  - 참고(FAIL 아님): 시료 검색이 ID+이름 대상인 점은 spec.md에 명시돼 있지 않음. `models/sample.py`의 `search_samples`가 더 이상 호출되지 않는 죽은 코드로 남아있음 — Phase 9(CleanCode)에서 정리 필요.
- 테스트: PASS (37개 전부 통과)

### plan-verify
- 전체 판정: PASS
- Phase 0, 2, 4: plan.md와 완전 일치 (브랜치/커밋 순서/메시지 형식).
- Phase 1, 3: 계획에 없던 [feat]/[test] 추가 작업 존재 — 구조적 이탈 아님, 각 기능의 자연스러운 확장.
  - Phase 1: 시료 검색 ID 지원, ID 중복 즉시 확인(`is_duplicate_sample_id`)
  - Phase 3: `list_reserved_orders` 컨트롤러 함수 추가
- 발견된 이슈: plan.md의 Phase 1 항목에 "이번 라운드는 Action까지만 진행, merge 보류"라는 메모가 남아있으나 실제로는 이미 `main`에 merge됨 (문서 지연) — 아래에서 수정함.

## 2026-07-15 — Phase 5~7

> 묶어서 실행한 사유: Skill이 이미 만들어져 있었음에도 Phase 5, 6, 7 각각의 merge 직전에 실행하지 않고 넘어감 — AI(Claude)의 누락. Phase 8에서야 뒤늦게 몰아서 실행함.

### harness-verify
- 정합성 검사: **FAIL → 수정 완료**
  - 실 생산량(shortage/actual_qty) 계산, 총 생산 시간, FIFO 큐, 생산 완료 시 재고 처리 순서(+actual_qty 후 -quantity), PRODUCING→CONFIRMED, 출고 CONFIRMED→RELEASE, main.py 메뉴 구성 — 전부 prd.md/spec.md와 일치.
  - **불일치(핵심 문제) 발견**: `controllers/production_controller.py`의 `complete_current_production()`이 진행률/경과 시간을 전혀 검사하지 않고 호출 즉시 완료 처리하여, spec.md의 "생산은 다 끝나야만 완료로 인정한다(중간에 일부만 완료된 것으로 치지 않는다)" 원칙을 위반함.
  - **조치**: `feature/생산완료-시간검증` 브랜치에서 TDD로 수정 — `elapsed_minutes < total_time`이면 `ValueError`를 발생시키도록 가드 추가, 생산 미시작(`production_started_at is None`) 상태에서 완료 시도해도 에러 처리. 관련 테스트 3개 추가 후 전부 통과 확인, `main`에 merge 완료(커밋 `2663756`, merge `055c564`).
  - 참고(FAIL 아님): `shortage`/`actual_qty` 계산이 spec.md 4.2(생산 라인) 담당으로 문서화되어 있으나 실제로는 `controllers/order_controller.py`의 승인 로직(4.1)에서 계산됨 — 재고 확인이 승인 시점에만 가능하므로 구조적으로 불가피한 배치이며 계산 결과 자체는 정확함. `models/order.py`의 `shortage`/`actual_qty`/`production_started_at` 필드가 spec.md 3.2 표에는 없음(문서 갱신 여지, 기능 문제 아님).
- 테스트: PASS (수정 후 49개 → CleanCode 정리 후 48개 전부 통과)

### plan-verify
- 전체 판정: PASS
- Phase 5, 6, 7 모두 브랜치/커밋 순서/메시지 형식이 계획과 일치.
- Phase 5는 계획된 5개 커밋 단위보다 더 잘게(8개) 나뉘었으나 TDD Red→Green 순서와 논리적 작업 순서는 계획과 동일 — 단순 세분화로 불일치 아님.
- harness-verify에서 발견된 버그 수정([test]/[fix], `feature/생산완료-시간검증`)은 계획에 없었지만 Phase 9 CleanCode/버그수정 범주로 정상 처리.

### CleanCode (Phase 9)
- `models/sample.py`의 미사용 `search_samples` 함수 및 관련 테스트 제거 (커밋 `b0177e6`).

## 2026-07-15 — Phase 10 (통합 검증 E2E)

- `main.py`를 통해 시료 2종 등록 → 재고충분 주문 승인(CONFIRMED) → 재고부족 주문 승인(PRODUCING) → 거절(REJECTED) → 생산 큐 FIFO 조회/진행률 확인 → 생산완료 처리(정상 완료 1건 + 아직 시간 안 지난 건 완료 시도 시 에러 정상 발생 확인) → 모니터링(재고 부족/여유 분류 정확) → 출고 처리(RELEASE)까지 하나의 흐름으로 실행.
- 종료 시 `EOFError`가 발생했으나, 이는 테스트 스크립트의 입력 줄이 부족해 stdin이 고갈된 것으로 애플리케이션 버그가 아님 (실제 대화형 사용 시에는 발생하지 않음).
- 최종 데이터 직접 조회로 검증: 주문 4건 상태(RELEASE 1 / CONFIRMED 1 / PRODUCING 1 / REJECTED 1) 및 재고값(S-001=10, S-002=500) 모두 기대값과 일치.
- 새로 발견된 버그 없음. Phase 8~9에서 고친 부분이 실제 통합 흐름에서도 올바르게 동작함을 확인.

## 2026-07-15 — Phase 10 이후 (사용성 개선, 앞단 검증, 헤더 통일/색상, README 등)

> 이 구간(Phase 11 사용성개선, `feature/메뉴헤더-포맷수정`, `feature/시료주문-앞단검증`, `feature/서브메뉴-헤더통일`, `feature/헤더색상-주황`, README/requirements.txt 작성)은 각 브랜치 merge 직후 검증을 실행하지 않고 사후에 몰아서 실행함. 앞으로는 merge 직후 바로 실행할 것.

### harness-verify
- 정합성 검사: PASS
  - `order_view.py`의 신규 앞단 존재확인이 `sample_view.py`의 기존 즉시확인 패턴과 구조적으로 일치, `is_duplicate_sample_id`를 반대 극성(존재해야 함 vs 존재하면 안 됨)으로 올바르게 재사용함 — 로직 오류 없음(다만 함수명이 order_view 문맥에서는 다소 오해 소지 있는 네이밍 스멜, CleanCode 대상으로 남겨둠).
  - `formatting.py`의 `_visible_len`/`_pad`가 ANSI 색상 코드를 제거하고 길이를 계산해 컬러 텍스트 포함 시에도 표 정렬이 깨지지 않음.
  - main.py + 6개 View 전부 `print_section_header`로 헤더 포맷 통일됨.
  - UX 변경이 상태 전이/도메인 로직을 건드리지 않았음(화면 표현만 변경).
- 테스트: PASS (49개 전부 통과)

### plan-verify
- 전체 판정: PASS
- Phase 11(사용성개선)은 계획된 3개 커밋 + FIFO 순서 테스트 1개(사용자 지적으로 추가) = 4개 커밋, plan.md 완료 기록과 일치.
- Phase 11 이후 4개 브랜치(`메뉴헤더-포맷수정`, `시료주문-앞단검증`, `서브메뉴-헤더통일`, `헤더색상-주황`)는 plan.md에 별도 Phase로 기록되지 않았으나, 각각 브랜치 분리 + `--no-ff` merge + CLAUDE.md 커밋 형식은 준수함. 사용자가 대화 중 즉석 요청한 소규모 UX 수정이라 매번 새 Phase를 만들 필요는 없다고 판단(합리적 예외).
- 참고: `aa7c71a` 커밋만 이 구간에서 예외적으로 "Phase 11:"을 표기했는데, Phase 11 완료 표기(`a7de762`) 이후 발생했고 Phase 11의 계획 범위에도 없는 별개 작업이라 라벨링이 다소 어긋남 — 이후 유사 작업엔 완료된 Phase 번호를 재사용하지 않을 것.
