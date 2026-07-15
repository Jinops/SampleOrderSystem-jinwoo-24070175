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
- **주의**: 이번 라운드는 구현(Action)까지만 진행하고 `main` merge는 보류한다 (사용자 지시).

### Phase 2~6 — 나머지 5개 기능 (Controller + View)

_Phase 1과 같은 형식으로, 시료 주문 → 주문 승인/거절 → 모니터링 → 생산 라인 조회 → 출고 처리 순서로 하나씩 이어서 작성_

### Phase 7 — 메인 메뉴 통합

_6개 기능 완료 후 작성_

- 메모(Phase 1에서 발견): Windows 콘솔 기본 코드페이지에서 한글 입출력이 깨지는 문제가 있었음(`PYTHONIOENCODING=utf-8`로 해결 확인). `main.py` 진입점에서 `sys.stdout.reconfigure(encoding="utf-8")` / `sys.stdin.reconfigure(encoding="utf-8")` 처리 필요.

### Phase 8 — Harness(검증) 단계

_문서-코드 정합성 검사 + 테스트 검증 subagent 실행 계획 작성_

### Phase 9 — CleanCode 정리

_Harness 결과를 바탕으로 리팩토링 계획 작성_
