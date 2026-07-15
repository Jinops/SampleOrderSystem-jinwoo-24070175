# SPEC — 반도체 시료 생산주문관리 시스템

`prd.md`에서 정의한 요구사항을 실제로 어떻게 구현할지 정리한 기술 스펙 문서.

## 1. 기술 스택

- 언어: **Python 3**
- 실행: 콘솔(터미널)에서 스크립트 직접 실행, 메뉴 번호를 입력받아 동작하는 루프 구조
- 영속성: 별도 DB 없이 **JSON 파일**로 시료/주문 데이터를 저장한다. 메모리 캐시를 두지 않고, 조회(Read)든 변경(Create/Update/Delete)이든 매 작업마다 JSON 파일을 직접 읽고 쓴다.
- 표준 라이브러리만 사용 (`dataclasses`, `enum`, `collections.deque`, `math`, `datetime`, `json` 등). 외부 패키지 의존 없음.

## 2. 아키텍처 (MVC)

**MVC(Model-View-Controller)** 패턴으로 구성한다.

```
main.py             # 진입점, 메인 메뉴 루프 (Controller로 라우팅)
models/             # Model — 데이터 클래스(Sample, Order, 상태 Enum) + JSON 파일 CRUD
views/              # View — 콘솔 출력 포맷팅, 사용자 입력 받기
controllers/        # Controller — 메뉴별 흐름 제어 + 도메인 로직(승인 분기, 생산량 계산, 상태 전이 등)
data/               # samples.json, orders.json 등 실제 데이터 파일
```

- **Model** (`models/`): `Sample`, `Order`, `OrderStatus` 데이터 구조를 정의하고, JSON 파일 read/write(CRUD)까지 Model의 책임으로 둔다. 메모리 캐시 없이 매 CRUD 호출마다 파일을 직접 읽고 쓴다.
- **View** (`views/`): 메뉴/결과 화면을 출력하고 사용자 입력을 받아 Controller에 전달한다. 판단 로직을 갖지 않는다.
- **Controller** (`controllers/`): `prd.md`의 기능 요구사항(승인 분기, 생산량 계산, 상태 전이 등)을 수행한다. View로부터 입력을 받아 Model을 조회/변경하고, 그 결과를 View에 넘겨 출력하게 한다.

이렇게 나누는 이유는 콘솔 출력 형식이 바뀌더라도 Controller/Model의 로직에 영향이 없도록 하기 위함이다.

## 3. 데이터 모델

### 3.1 Sample (시료)

| 필드 | 타입 | 설명 |
|---|---|---|
| `sample_id` | str | 시료 고유 ID (예: `S-001`) |
| `name` | str | 시료명 |
| `avg_process_time` | float | 평균 생산시간 (분/개) |
| `yield_rate` | float | 수율 (0~1 사이 값) |
| `stock` | int | 현재 재고 수량 |

### 3.2 Order (주문)

| 필드 | 타입 | 설명 |
|---|---|---|
| `order_id` | str | 주문 번호 (예: `ORD-20260416-0043`) |
| `sample_id` | str | 대상 시료 ID |
| `customer_name` | str | 고객명 |
| `quantity` | int | 주문 수량 |
| `status` | OrderStatus | 아래 3.3 참고 |
| `created_at` | datetime | 주문 생성 시각 |

### 3.3 OrderStatus (Enum)

```
RESERVED    # 접수, 승인 대기
REJECTED    # 거절
PRODUCING   # 승인 완료, 재고 부족으로 생산 중
CONFIRMED   # 승인 완료(또는 생산 완료), 출고 대기
RELEASE     # 출고 완료
```

상태 전이는 `prd.md` 4장의 전이도를 그대로 따르며, 전이 로직은 `controllers` 계층에서만 수행한다 (Model이나 View에서 직접 상태를 바꾸지 않는다).

### 3.4 영속성 (JSON)

- `data/samples.json`, `data/orders.json` 두 개 파일로 분리 저장한다.
- 저장 형식: 각 파일은 객체 리스트를 담은 JSON 배열. `Order`의 `status`는 문자열(Enum의 `value`)로, `created_at`은 ISO 8601 문자열로 직렬화한다.
- 메모리 캐시 없음: `models`는 상태를 들고 있지 않는다.
  - 조회(목록/검색 등): 호출될 때마다 해당 JSON 파일을 읽어 그 자리에서 반환한다.
  - 등록/수정(시료 등록, 주문 생성/승인/거절/생산완료/출고 등): 호출될 때마다 JSON 파일을 읽고 → 메모리 상에서 변경 → 즉시 다시 파일에 씀, 이 세 단계를 한 번의 CRUD 호출 안에서 수행한다.
- 파일이 없으면 빈 목록으로 간주하고 새로 생성한다.

## 4. 핵심 로직

### 4.1 주문 승인 (`controllers.order`)

1. `RESERVED` 상태 주문을 대상으로 승인/거절 입력을 받는다.
2. 거절 시 → `REJECTED`로 전환하고 종료.
3. 승인 시 재고를 확인한다.
   - `order.quantity <= sample.stock` → 재고 차감 후 `CONFIRMED`로 전환.
   - 재고 부족 → 부족분(`shortage = quantity - stock`)을 계산해 생산 큐에 등록하고 `PRODUCING`으로 전환.

### 4.2 생산 라인 (`controllers.production`)

- 생산 큐는 `collections.deque`로 구현, **FIFO**로 처리한다.
- 실 생산량: `actual_qty = ceil(shortage / yield_rate)`
- 총 생산 시간: `total_time = avg_process_time * actual_qty`
- 생산 완료 처리 시:
  - 해당 시료의 재고를 `actual_qty`만큼 증가시킨 뒤, 주문 수량만큼 다시 차감한다 (즉 재고에는 초과 생산분만 남는다).
  - 주문 상태를 `PRODUCING → CONFIRMED`로 전환한다.
- 큐 조회 시 "현재 처리 중 1건 + 대기 중 목록"을 함께 보여준다 (`prd.md` 5.5 참고).

### 4.3 모니터링 (`controllers.monitoring`)

- 주문량 확인: 전체 주문을 `status`별로 그룹핑해 건수 집계. `REJECTED`는 집계 대상에서 제외.
- 재고량 확인: 시료별 재고 수준을 아래 기준으로 분류.
  - `stock == 0` → 고갈
  - 해당 시료에 대해 대기 중(`RESERVED`/`PRODUCING`)인 주문 수량 합계보다 재고가 적으면 → 부족
  - 그 외 → 여유

### 4.4 출고 처리 (`controllers.shipment`)

- `CONFIRMED` 상태 주문 목록에서 하나를 선택해 출고 처리.
- 처리 시 주문 상태를 `CONFIRMED → RELEASE`로 전환.

## 5. 메인 메뉴 구조

```
[1] 시료 관리       — 등록 / 목록 조회 / 검색
[2] 시료 주문       — 신규 주문(RESERVED) 생성
[3] 주문 승인/거절  — RESERVED 목록 → 승인/거절
[4] 모니터링        — 주문량 확인 / 재고량 확인
[5] 생산라인 조회   — 현재 생산 중 + 대기열(FIFO)
[6] 출고 처리       — CONFIRMED → RELEASE
[0] 종료
```

각 메뉴는 `controllers/` 하위의 개별 컨트롤러가 담당하고, 대응하는 `views/` 모듈을 통해 화면을 그린다. 메인 루프(`main.py`)는 메뉴 번호에 따라 해당 컨트롤러를 호출하는 역할만 한다.

## 6. 에러 처리 원칙

- 잘못된 메뉴 번호, 존재하지 않는 시료/주문 ID 입력 등은 예외를 발생시키지 않고 안내 메시지를 출력한 뒤 해당 메뉴를 다시 보여준다.
- 수량 등 숫자 입력값 검증은 `views` 계층에서 1차로 수행한다.
