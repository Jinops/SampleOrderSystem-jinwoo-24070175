---
name: harness-verify
description: Phase를 main에 merge하기 전, 문서-코드 정합성과 테스트 통과 여부를 자동으로 검증하는 Harness. "harness 검증", "phase 검증", "머지 전 확인해줘" 같은 요청에 사용한다.
---

# Harness Verify

사용자가 방금 구현한 결과를, 사람이 최종 리뷰하기 전에 먼저 자동으로 검증하는 단계다. `prd.md`/`spec.md`의 요구사항과 실제 코드가 어긋나지 않는지, 그리고 테스트가 실제로 통과하는지 확인한다.

## 실행 순서

1. 아래 두 검증을 **각각 별도 subagent(Agent tool, subagent_type: "general-purpose")로 병렬 실행**한다.

   **검증 A — 문서-코드 정합성 검사**
   - `prd.md`, `spec.md`를 읽고, 이번 Phase에서 변경된 파일(`git diff` 대상)을 읽는다.
   - 주문 상태값, 전이 규칙, 계산식(실 생산량 = ceil(부족분/수율) 등), 필드명 등이 문서와 실제 구현에서 일치하는지 확인한다.
   - 불일치가 있으면 파일:라인과 함께 구체적으로 보고한다.

   **검증 B — 테스트 통과 확인**
   - `python -m pytest tests/ -v`를 실행한다.
   - 실패한 테스트가 있으면 어떤 테스트가 왜 실패했는지 보고한다.

2. 두 subagent의 결과를 취합해서 아래 형식으로 요약 보고한다.
   - 정합성 검사: PASS/FAIL (FAIL이면 구체적 불일치 목록)
   - 테스트: PASS/FAIL (FAIL이면 실패 테스트 목록)
   - 종합 판단: 이 Phase를 `main`에 merge해도 되는지 여부

3. 종합 판단이 FAIL이면, merge하지 말고 먼저 사용자에게 보고한다. PASS면 평소 워크플로우대로 merge를 진행해도 된다고 안내한다.

## 언제 사용하는가

- 각 Phase의 Action(구현)이 끝나고, `feature/*` 브랜치를 `main`에 merge하기 전.
- Phase 8(Harness 단계)에서는 지금까지의 모든 Phase에 대해 한 번 더 전체적으로 실행한다.
