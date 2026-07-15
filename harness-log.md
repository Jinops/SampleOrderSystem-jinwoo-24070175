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
