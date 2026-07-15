# PLAN — 반도체 시료 생산주문관리 시스템

`prd.md`/`spec.md`를 바탕으로 실제 구현 순서를 정리한 계획 문서.

## 1. 거시적 계획 (Macro Plan)

전체 개발은 `spec.md`의 MVC 계층(Model → Controller → View) 순서를 따르되, **TDD(테스트 주도 개발)** 로 진행한다. 즉 로직이 있는 부분은 "테스트 작성(Red) → 최소 구현으로 통과(Green) → 리팩토링(Refactor)" 순서를 기본 사이클로 삼는다.

1. **Model 구현 (TDD, 공통 기반 — 가로로 한 번에)** — `Sample`, `Order`, `OrderStatus`(Enum) 데이터 클래스와 JSON 파일(`data/samples.json`, `data/orders.json`) 기반 CRUD를 만든다. 모든 기능이 공유하는 데이터 구조이므로 기능별로 쪼개지 않고 전체를 한 번에 완성한다. CRUD 동작(저장/조회 시 데이터 정합성)에 대한 테스트를 먼저 작성한 뒤 구현한다.
2. **기능별 Controller + View 구현 (TDD, 세로로 관통)** — Model이 준비된 뒤에는 아래 6개 기능을 하나씩 순서대로, 각 기능마다 Controller와 View를 함께 완성해나간다.
   1. 시료 관리
   2. 시료 주문
   3. 주문 승인/거절
   4. 모니터링
   5. 생산 라인 조회
   6. 출고 처리

   기능마다 상태 전이·계산식(실 생산량, 재고 분류 등) 테스트를 먼저 작성한 뒤 Controller 로직을 구현하고, 그 위에 View(콘솔 출력/입력)를 붙인다. View는 단순 입출력 위주라 TDD를 강제하지 않고 구현 후 수동 확인으로 진행한다.
3. **메인 메뉴 통합** — 6개 기능이 모두 완성된 뒤, `main.py`에서 6개 메뉴 + 종료를 라우팅하는 루프를 완성해 하나의 실행 가능한 프로그램으로 묶는다.
4. **Harness(검증) 단계** — 사람이 최종 확인하기 전에, 아래 두 가지를 subagent로 자동 검증한다.
   - 문서-코드 정합성 검사: 구현이 `prd.md`/`spec.md`의 요구사항·상태 전이·계산식과 실제로 일치하는지 확인
   - 테스트 검증: 1~2단계에서 TDD로 쌓인 pytest 테스트가 실제로 전부 통과하는지 확인
5. **정리 (CleanCode)** — Harness 검증 결과 나온 이슈를 반영해 가독성/중복 제거 등 리팩토링한다. (TDD의 Refactor 단계에서 못다 한 정리를 포함)

### 진행 방식

- Model은 공통 기반이라 가로로(전체를 한 번에) 만들고, Controller+View는 기능 단위로 세로 관통해서(하나의 기능을 Controller부터 View까지 완성) 진행한다.
- 각 기능은 `feature/기능명` 브랜치에서 개발한 뒤 `main`에 merge한다 (`CLAUDE.md` 브랜치 전략 참고).
- 커밋은 기능 단위로 잘게 나누어 남긴다 (`CLAUDE.md` 커밋 룰 참고). TDD 사이클(Red/Green/Refactor) 전체를 기능 하나의 커밋 단위로 묶을지, 사이클별로 더 잘게 나눌지는 Phase별 계획에서 정한다.

## 2. Phase별 세부 계획

### Phase 0 — Model 계층

목표: `Sample`/`Order`/`OrderStatus`와 JSON 기반 CRUD를 완성해, 이후 모든 Controller가 딛고 설 수 있는 공통 기반을 만든다.

- 브랜치: `feature/model-layer`
- 작업 순서 (TDD, Red → Green 반복):
  1. `models/enums.py` — `OrderStatus` Enum(`RESERVED`/`REJECTED`/`PRODUCING`/`CONFIRMED`/`RELEASE`) 정의. 로직이 없으므로 별도 테스트 없이 바로 작성.
  2. `models/sample.py` — `Sample` dataclass(`sample_id`/`name`/`avg_process_time`/`yield_rate`/`stock`) 정의 + `data/samples.json` 대상 CRUD 함수(`list_samples`, `get_sample`, `save_sample`, `search_samples`).
     - 테스트 먼저 (`tests/test_sample_model.py`, `tmp_path` fixture로 실제 `data/`와 분리): 등록 후 조회 시 값이 그대로 나오는지, 재고 수정 후 다시 읽으면 갱신된 값이 보이는지, 존재하지 않는 ID 조회 시 처리.
  3. `models/order.py` — `Order` dataclass(`order_id`/`sample_id`/`customer_name`/`quantity`/`status`/`created_at`) 정의 + `data/orders.json` 대상 CRUD 함수(`list_orders`, `get_order`, `save_order`).
     - 테스트 먼저 (`tests/test_order_model.py`): 생성 시 `status`가 `RESERVED`로 저장/복원되는지, `created_at`이 ISO 8601로 직렬화·역직렬화되는지, 상태값 변경 후 재조회 시 반영되는지.
  4. 파일이 없을 때(첫 실행) 빈 리스트로 시작하는 경우에 대한 테스트 + 구현.
- 커밋 단위 (기능 단위로 잘게, `CLAUDE.md` 규칙 — Phase 표기 포함):
  1. `[test] Phase 0: Sample 모델 CRUD 테스트 작성`
  2. `[feat] Phase 0: Sample 모델 및 JSON CRUD 구현`
  3. `[test] Phase 0: Order 모델 CRUD 테스트 작성`
  4. `[feat] Phase 0: Order 모델 및 JSON CRUD 구현`
  5. (필요 시) `[refact] Phase 0: Model 계층 정리`
- 완료 기준: `pytest tests/test_sample_model.py tests/test_order_model.py`가 전부 통과, `feature/model-layer`를 `main`에 merge.
- **완료됨** — `main`에 merge 완료 (2026-07-15).

### Phase 1 — 시료 관리 (Controller + View)

목표: Phase 0의 `models/sample.py` 위에 "시료 등록 / 조회 / 검색" 기능을 완성한다 (`prd.md` 5.1).

- 브랜치: `feature/시료-관리`
- 작업 순서 (TDD):
  1. `controllers/sample_controller.py` — `register_sample()`, `list_samples()`, `search_samples()` 구현. 중복 시료 ID 등록 방지, 수율(`yield_rate`)이 0~1 범위인지 등 입력 검증 포함.
     - 테스트 먼저 (`tests/test_sample_controller.py`): 정상 등록/조회/검색, 중복 ID 등록 시 에러 처리, 수율 범위를 벗어난 값 등록 시 에러 처리.
  2. `views/sample_view.py` — 하위 메뉴 `[1] 시료 등록 / [2] 시료 목록 / [3] 시료 검색 / [0] 뒤로` 출력, 입력 받아 Controller 호출, 결과를 표 형태로 출력(`prd.md` 예시 UI 참고). 단순 입출력이라 TDD 없이 구현 후 수동 확인.
- 커밋 단위:
  1. `[test] Phase 1: 시료 등록/조회/검색 컨트롤러 테스트 작성`
  2. `[feat] Phase 1: 시료 관리 컨트롤러 구현`
  3. `[feat] Phase 1: 시료 관리 콘솔 View 구현`
- 완료 기준: `pytest tests/test_sample_controller.py` 통과, 콘솔에서 `[1] 시료 관리` 메뉴가 정상 동작, `feature/시료-관리`를 `main`에 merge.
- **완료됨** — `main`에 merge 완료 (2026-07-15).

### Phase 2 — 시료 주문 (Controller + View)

목표: 고객 요청을 받아 주문(예약)을 생성하는 기능을 완성한다 (`prd.md` 5.2).

- 브랜치: `feature/시료-주문`
- 작업 순서 (TDD):
  1. `controllers/order_controller.py` — `create_order(sample_id, customer_name, quantity)` 구현.
     - 존재하지 않는 시료 ID로 주문하면 에러 (`prd.md`: "시스템에 등록된 시료만 주문 가능").
     - 수량이 1 이상의 정수가 아니면 에러.
     - 주문번호는 `ORD-YYYYMMDD-NNNN` 형식으로 자동 생성 (당일 주문 건수 기준 순번).
     - 생성 직후 상태는 `RESERVED`.
     - 테스트 먼저 (`tests/test_order_controller.py`).
  2. `views/order_view.py` — 시료 ID / 고객명 / 수량을 입력받아 `create_order` 호출, 결과(주문번호/상태) 출력. TDD 없이 구현 후 수동 확인.
- 커밋 단위:
  1. `[test] Phase 2: 시료 주문 생성 컨트롤러 테스트 작성`
  2. `[feat] Phase 2: 시료 주문 생성 컨트롤러 구현`
  3. `[feat] Phase 2: 시료 주문 콘솔 View 구현`
- 완료 기준: `pytest tests/test_order_controller.py` 통과, 콘솔에서 `[2] 시료 주문` 메뉴가 정상 동작, `feature/시료-주문`을 `main`에 merge.

### Phase 3 — 주문 승인/거절 (Controller + View)

목표: `RESERVED` 주문을 승인/거절 처리한다 (`prd.md` 5.3, `spec.md` 4.1).

- 브랜치: `feature/주문-승인거절`
- 작업 순서 (TDD):
  1. `controllers/order_controller.py`에 함수 추가 — `approve_order(order_id)`, `reject_order(order_id)`.
     - `approve_order`: 대상 주문이 `RESERVED`가 아니면 에러. 재고가 주문 수량 이상이면 재고 차감 후 `CONFIRMED`로 전환. 재고가 부족하면 재고는 그대로 두고 `PRODUCING`으로 전환 (실제 생산 처리는 Phase 5에서 다룸 — "생산 큐"는 별도 자료구조 없이 `status == PRODUCING`인 주문을 `created_at` 기준 FIFO로 조회하는 것으로 대체한다).
     - `reject_order`: 대상 주문이 `RESERVED`가 아니면 에러. 즉시 `REJECTED`로 전환.
     - 테스트 먼저 (`tests/test_order_approval.py`): 재고 충분 승인 시 CONFIRMED+재고 차감, 재고 부족 승인 시 PRODUCING(+재고 불변), 거절 시 REJECTED, RESERVED가 아닌 주문에 승인/거절 시도하면 에러.
  2. `views/order_approval_view.py` — `RESERVED` 주문 목록을 보여주고 번호 선택 후 승인/거절(Y/N)을 입력받아 처리 결과를 출력. TDD 없이 구현 후 수동 확인.
- 커밋 단위:
  1. `[test] Phase 3: 주문 승인/거절 컨트롤러 테스트 작성`
  2. `[feat] Phase 3: 주문 승인/거절 컨트롤러 구현`
  3. `[feat] Phase 3: 주문 승인/거절 콘솔 View 구현`
- 완료 기준: `pytest tests/test_order_approval.py` 통과, 콘솔에서 `[3] 주문 승인/거절` 메뉴가 정상 동작, `feature/주문-승인거절`을 `main`에 merge.

### Phase 4 — 모니터링 (Controller + View)

목표: 주문량/재고량 현황을 확인하는 조회 전용 기능을 완성한다 (`prd.md` 5.4, `spec.md` 4.3).

- 브랜치: `feature/모니터링`
- 작업 순서 (TDD):
  1. `controllers/monitoring_controller.py`:
     - `count_orders_by_status()` — 전체 주문을 상태별(`RESERVED`/`CONFIRMED`/`PRODUCING`/`RELEASE`)로 집계. `REJECTED`는 제외.
     - `classify_sample_stock()` — 시료별 현재 재고와 함께, 그 시료에 대해 아직 처리 중인 주문(`RESERVED`+`PRODUCING`) 수량 합계 대비 재고 수준을 `여유`/`부족`/`고갈` 3단계로 분류. 재고 0이면 무조건 `고갈`, 대기 수량 합이 재고보다 많으면 `부족`, 그 외 `여유`.
     - 테스트 먼저 (`tests/test_monitoring.py`): 상태별 집계에서 REJECTED 제외 확인, 여유/부족/고갈 각 케이스.
  2. `views/monitoring_view.py` — `[1] 주문량 확인 / [2] 재고량 확인 / [0] 뒤로` 하위 메뉴. TDD 없이 구현 후 수동 확인.
- 커밋 단위:
  1. `[test] Phase 4: 모니터링 컨트롤러 테스트 작성`
  2. `[feat] Phase 4: 모니터링 컨트롤러 구현`
  3. `[feat] Phase 4: 모니터링 콘솔 View 구현`
- 완료 기준: `pytest tests/test_monitoring.py` 통과, 콘솔에서 `[4] 모니터링` 메뉴가 정상 동작, `feature/모니터링`을 `main`에 merge.

### Phase 5 — 생산 라인 조회 (Controller + View)

목표: `PRODUCING` 주문의 생산 큐를 조회하고, 생산 완료 처리를 한다 (`prd.md` 5.5, `spec.md` 4.2).

- 브랜치: `feature/생산라인`
- 설계 결정:
  - `models/order.py`의 `Order`에 `shortage`(부족분), `actual_qty`(실 생산량), `production_started_at`(생산 시작 시각) 3개 필드를 nullable로 추가한다.
  - `shortage`/`actual_qty`는 승인 시점(`controllers/order_controller.approve_order`가 `PRODUCING`으로 전환하는 순간)에 계산해서 주문에 저장한다 — 이후 재고가 바뀌어도 이 값은 고정.
  - 생산 큐는 `status == PRODUCING`인 주문을 `created_at` 기준 FIFO로 정렬한 것. 맨 앞 주문이 "현재 처리 중"이며, 처음 조회되는 시점에 `production_started_at`을 기록한다(없으면 지금 시각으로 설정).
  - 진행률(progress bar)은 `spec.md`에서 정한 대로 표시 전용이며, 실제 재고/상태 반영과는 무관하다. 생산 완료 처리는 시간 경과를 자동으로 검사하지 않고, 담당자가 메뉴에서 "생산완료 처리"를 실행하는 시점에 큐 맨 앞 주문 1건을 완료 처리한다(콘솔 데모 특성상 실시간 대기를 강제하지 않음). `PRODUCING`과 `CONFIRMED` 사이에는 다른 상태가 없으므로 "중간에 일부만 완료"라는 상태 자체가 존재하지 않는다.
- 작업 순서 (TDD):
  1. `models/order.py` 필드 추가 + 직렬화 — 테스트 먼저 (`tests/test_order_model.py`에 케이스 추가).
  2. `controllers/order_controller.py`의 `approve_order`가 `PRODUCING` 전환 시 `shortage`/`actual_qty`를 계산해 저장하도록 수정 — 테스트 먼저 (`tests/test_order_approval.py`에 케이스 추가).
  3. `controllers/production_controller.py`:
     - `get_production_queue()` — FIFO 큐 + 맨 앞 주문의 진행률/완료 예정 시각 + 나머지 주문의 누적 예상 완료 시각.
     - `complete_current_production()` — 큐 맨 앞 주문을 완료 처리 (재고 `actual_qty`만큼 증가 후 주문 수량만큼 차감, 상태 `PRODUCING → CONFIRMED`). 큐가 비어있으면 에러.
     - 테스트 먼저 (`tests/test_production.py`).
  4. `views/production_view.py` — 큐 조회 화면(진행률 바 텍스트 출력) + 완료 처리 메뉴. TDD 없이 구현 후 수동 확인.
- 커밋 단위:
  1. `[test] Phase 5: Order에 shortage/actual_qty/production_started_at 필드 테스트 작성`
  2. `[feat] Phase 5: Order 모델 필드 추가 및 승인 시 shortage/actual_qty 계산 반영`
  3. `[test] Phase 5: 생산 큐 조회 및 완료 처리 컨트롤러 테스트 작성`
  4. `[feat] Phase 5: 생산 라인 컨트롤러 구현`
  5. `[feat] Phase 5: 생산 라인 콘솔 View 구현`
- 완료 기준: `pytest tests/test_production.py` 통과, 콘솔에서 `[5] 생산라인 조회` 메뉴가 정상 동작, `feature/생산라인`을 `main`에 merge.

### Phase 6 — 출고 처리 (Controller + View)

목표: `CONFIRMED` 주문을 선택해 출고 처리한다 (`prd.md` 5.6, `spec.md` 4.4).

- 브랜치: `feature/출고처리`
- 작업 순서 (TDD):
  1. `controllers/shipment_controller.py` — `list_confirmed_orders()`, `ship_order(order_id)`. `ship_order`는 대상 주문이 `CONFIRMED`가 아니면 에러, 맞으면 `RELEASE`로 전환.
     - 테스트 먼저 (`tests/test_shipment.py`).
  2. `views/shipment_view.py` — `CONFIRMED` 목록 표시 후 번호 선택 → 출고 처리. TDD 없이 구현 후 수동 확인.
- 커밋 단위:
  1. `[test] Phase 6: 출고 처리 컨트롤러 테스트 작성`
  2. `[feat] Phase 6: 출고 처리 컨트롤러 구현`
  3. `[feat] Phase 6: 출고 처리 콘솔 View 구현`
- 완료 기준: `pytest tests/test_shipment.py` 통과, 콘솔에서 `[6] 출고 처리` 메뉴가 정상 동작, `feature/출고처리`를 `main`에 merge.

### Phase 7 — 메인 메뉴 통합

목표: 6개 기능 View를 하나의 실행 가능한 콘솔 프로그램(`main.py`)으로 묶는다 (`prd.md` 3장/5장 메인 메뉴).

- 브랜치: `feature/메뉴통합`
- 작업 순서:
  1. `main.py` — 시스템 현황(등록 시료 수/총 재고/전체 주문 수/생산라인 대기 건수) 출력 + `[1]~[6]`, `[0] 종료` 메뉴 라우팅 루프. 각 메뉴는 대응하는 `views.*.run()`을 호출.
  2. Phase 1에서 발견한 인코딩 이슈 해결: 진입점에서 `sys.stdout.reconfigure(encoding="utf-8")` / `sys.stdin.reconfigure(encoding="utf-8")` 처리.
  3. 단순 라우팅/출력 로직이라 TDD 없이 구현 후 전체 메뉴를 한 바퀴 수동으로 순회하며 확인.
- 커밋 단위:
  1. `[feat] Phase 7: main.py 메인 메뉴 통합 구현`
- 완료 기준: `python main.py` 실행 후 6개 메뉴 모두 진입 가능, 콘솔 인코딩 문제 없음, `feature/메뉴통합`을 `main`에 merge.

### Phase 8 — Harness(검증) 단계

목표: Phase 0~7 전체에 대해 `harness-verify`/`plan-verify` Skill을 한 번 더 전체적으로 실행해 최종 확인한다.

- 별도 feature 브랜치 없이 `main`에서 직접 실행 (코드 변경이 아닌 검증 작업이므로).
- `harness-verify`: 전체 `models`/`controllers`/`views`가 `prd.md`/`spec.md`와 일치하는지, 전체 테스트가 통과하는지 확인.
- `plan-verify`: Phase 5~7의 계획 대비 실제 진행(브랜치/커밋/완료기준)을 확인 (Phase 0~4는 이미 한 차례 검증 완료).
- FAIL 항목이 있으면 Phase 9에서 정리한다.
- **완료됨** — harness-verify에서 생산완료 처리가 시간 경과를 검증하지 않는 spec 위반(FAIL) 1건 발견 → `feature/생산완료-시간검증`에서 즉시 수정(TDD) 후 재검증 PASS. plan-verify(Phase 5~7)는 PASS.

### Phase 9 — CleanCode 정리

목표: Harness 검증에서 발견된 이슈와 그 외 가독성/중복 문제를 정리한다.

- 별도 feature 브랜치 없이 `main`에서 직접 작업 (기능 추가가 아닌 정리이므로 `[refact]`/`[chore]` 커밋 위주).
- 확인된 정리 대상: `models/sample.py`의 미사용 `search_samples` 함수 제거.
- Phase 8에서 새로 발견된 이슈가 있으면 함께 정리.
- 정리 후 전체 테스트가 여전히 통과하는지 재확인.
- **완료됨** — 미사용 `search_samples`(models/sample.py) 및 관련 테스트 제거(커밋 `b0177e6`). Phase 8에서 발견된 생산완료 버그는 별도 `[fix]`로 즉시 수정(위 Phase 8 참고). 전체 테스트 48개 통과 확인.

### Phase 10 — 통합 검증 (End-to-End)

목표: 지금까지는 각 기능(View)을 개별적으로만 스모크 테스트했다. `main.py`를 통해 등록→주문→승인/거절→생산→출고까지 하나의 흐름으로 이어서 실행했을 때도 문제없이 동작하는지 확인한다. 이 과정에서 버그가 발견되면 TDD로 즉시 수정한다.

- 별도 feature 브랜치 없이 `main`에서 직접 검증 (신규 기능 개발이 아닌 검증 작업이므로).
- 검증 시나리오:
  1. 시료 등록 (재고를 일부러 적게 설정해 이후 재고 부족 케이스도 함께 확인)
  2. 재고보다 적은 수량 주문 → 승인 → 재고 충분 경로(CONFIRMED) 확인
  3. 재고보다 많은 수량 주문 → 승인 → 재고 부족 경로(PRODUCING) 확인
  4. 생산라인 조회로 큐/진행률 확인 → 생산 미완료 상태에서 완료 시도 시 에러 확인(Phase 9에서 고친 가드 재확인)
  5. 시간 조건을 만족시킨 뒤(또는 테스트용으로 평균 생산시간 0인 시료로) 생산 완료 처리 → CONFIRMED 전환 확인
  6. 모니터링에서 주문량/재고량 현황이 실제 상태를 정확히 반영하는지 확인
  7. 출고 처리로 RELEASE까지 전환 확인
  8. 거절(REJECTED) 케이스도 한 번 확인
- 버그 발견 시 처리: 원인이 되는 계층(model/controller/view)에 TDD로 테스트를 먼저 추가(Red) → 수정(Green) → 커밋. 커밋 메시지는 `[fix] Phase 10: ...` 형식.
- 완료 기준: 위 8개 시나리오가 `main.py` 상에서 모두 정상 동작하고, `pytest tests/` 전체가 통과.
- **완료됨** — `main.py`로 시료 2종 등록 → 재고충분/부족 주문 승인(CONFIRMED/PRODUCING 분기) → 거절 → 생산 큐 FIFO 조회·진행률 → 생산완료(정상)/생산완료(시간 미충족 에러) → 모니터링(재고 부족/여유 분류) → 출고(RELEASE) 전체 흐름을 한 번에 실행. 최종 주문 상태(RELEASE/CONFIRMED/PRODUCING/REJECTED)와 재고값을 직접 조회해 계산이 모두 정확함을 확인. 새로 발견된 버그 없음.

### Phase 11 — 사용성 개선 (시각화, UX 개선 등)

목표: 기능은 다 갖춰졌으니, 콘솔 화면의 가독성/시각적 표현을 개선한다.

- 브랜치: `feature/사용성개선`
- 확정된 범위 (사용자 선택): **① 상태값 강조 표시(색상/기호)**, **② 테이블/메뉴 레이아웃 정리**
- 작업 순서:
  1. `views/formatting.py` 공통 모듈 신설
     - 주문 상태(RESERVED/CONFIRMED/PRODUCING/RELEASE/REJECTED)와 재고 상태(여유/부족/고갈)를 ANSI 색상으로 감싸는 `colorize(text, key)` 함수.
     - 표 형태 출력을 일관된 폭/구분선으로 그려주는 `print_table(headers, rows, widths)` 함수.
  2. 기존 5개 View(`sample_view`, `order_view`, `order_approval_view`, `monitoring_view`, `production_view`, `shipment_view`)에서 상태값 출력과 표 출력을 `formatting.py` 함수로 교체.
  3. `main.py`의 헤더/메뉴 구분선도 동일한 스타일로 정리.
- 단순 출력/포맷 개선이라 TDD 없이 구현 후 수동 확인 위주로 진행. 기존 pytest는 출력 포맷을 검사하지 않으므로 그대로 통과해야 함.
- 커밋 단위:
  1. `[feat] Phase 11: views/formatting.py 공통 색상/테이블 출력 모듈 구현`
  2. `[refact] Phase 11: 각 View가 formatting.py를 사용하도록 정리`
  3. `[refact] Phase 11: main.py 헤더/메뉴 레이아웃 정리`
- 완료 기준: `main.py` 전체 메뉴를 한 바퀴 돌며 상태값 색상 표시와 정돈된 표가 정상 출력되는지 확인, `pytest tests/` 전체 통과, `feature/사용성개선`을 `main`에 merge.
- **완료됨** — ANSI 색상(RESERVED 노랑/CONFIRMED 초록/PRODUCING 청록/RELEASE 보라/REJECTED 빨강, 여유 초록/부족 노랑/고갈 빨강)과 공통 테이블 포맷을 6개 View에 전부 적용. `cat -v`로 ANSI 코드 정상 출력 및 정렬 확인. 겸사겸사 "생산 큐에 여러 건이 쌓여있을 때 순서대로 완료 처리되는지"를 검증하는 테스트도 추가(사용자 지적으로 발견된 커버리지 공백, 기존 구현이 이미 올바르게 동작함을 확인). 테스트 49개 전부 통과.
