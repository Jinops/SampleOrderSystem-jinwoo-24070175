# 반도체 시료 생산주문관리 시스템

가상의 반도체 회사 S-Semi가 시료(Sample) 주문·생산·출고를 관리하는 콘솔 기반 프로그램입니다.

## 실행 방법

```bash
pip install -r requirements.txt   # 테스트 실행용 (pytest). 앱 자체는 외부 의존성 없음
python main.py
```

## 개발 방식 — Agentic Engineering

Claude Code와 함께 아래 4단계 워크플로우를 반복하며 개발했습니다 (`CLAUDE.md` 참고).

1. **Explore** — `prd.md`/`spec.md`로 요구사항·기술 스펙을 먼저 정리
2. **Plan** — `plan.md`에 거시적 계획 + Phase별(0~11) 세부 계획 수립
3. **Action** — Phase마다 `feature/*` 브랜치에서 TDD(Red→Green)로 구현
4. **Commit** — Phase 단위로 잘게 커밋(`[type] Phase N: 내용`), `main`에 merge

이 흐름을 12개 Phase(Model → 6개 기능 → 메뉴 통합 → Harness 검증 → CleanCode → 통합 검증 → 사용성 개선)에 걸쳐 반복했고, 과정은 전부 git 커밋 히스토리에 남아있습니다.

## 문서 구성

| 파일 | 역할 |
|---|---|
| `CLAUDE.md` | 워크플로우, 커밋 규칙, 브랜치 전략 등 운영 규칙 |
| `prd.md` | 제품 요구사항 (무엇을 만드는가) |
| `spec.md` | 기술 스펙 (아키텍처, 데이터 모델, 핵심 로직) |
| `plan.md` | 거시적 계획 + Phase 0~11 세부 계획/진행 기록 |
| `harness-log.md` | 검증(Harness) 실행 이력 |

## Agent(서브에이전트) 활용 — Harness

과제 요구사항의 "Harness 도입"을 만족시키기 위해, 구현이 끝날 때마다 사람이 최종 확인하기 전 **서브에이전트로 자동 검증**하는 단계를 뒀습니다.

- `.claude/skills/harness-verify` — ① 문서-코드 정합성 검사, ② 테스트 통과 여부를 각각 별도 서브에이전트로 병렬 실행
- `.claude/skills/plan-verify` — `plan.md`에 적은 계획(브랜치/커밋 단위/완료 기준)과 실제 git 히스토리가 일치하는지 검증

실행 결과는 전부 `harness-log.md`에 누적 기록했고, 실제로 이 과정에서 스펙 위반 버그 1건을 발견해 즉시 수정했습니다.

## 품질 관리 — Test / CleanCode

- **Test**: 기능 구현 전 테스트를 먼저 작성하는 TDD(Red → Green)로 진행, `tests/`에 49개 pytest 테스트 작성
- **CleanCode**: Harness 검증에서 발견된 죽은 코드(미사용 `search_samples` 등)를 별도 `[refact]` 커밋으로 정리, 검증 이력은 `harness-log.md`에 기록

## 구현 기능

- **시료 관리** — 등록 / 조회 / 검색 (ID·이름 검색, 중복 ID 즉시 확인)
- **시료 주문** — 신규 주문 생성
- **주문 승인/거절** — 재고 충분/부족에 따른 자동 분기 처리
- **모니터링** — 상태별 주문량 확인, 재고 수준(여유/부족/고갈) 확인
- **생산 라인 조회** — FIFO 생산 큐, 진행률 표시, 생산 완료 처리
- **출고 처리** — 완료된 주문 출고

## 기술 스택

- Python 3 (표준 라이브러리만 사용, 외부 런타임 의존성 없음)
- JSON 파일 기반 영속성 (`data/samples.json`, `data/orders.json`)
- MVC 패턴 (`models/` · `views/` · `controllers/`)
- TDD + pytest (49개 테스트)
