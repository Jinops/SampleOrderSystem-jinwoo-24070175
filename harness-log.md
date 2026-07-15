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
> Phase 4 개발 이후 하네스 개발하여, 0~4 통합 진행
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
