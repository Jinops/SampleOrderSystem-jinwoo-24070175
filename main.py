import sys
from datetime import datetime

from controllers.order_controller import list_orders
from controllers.production_controller import get_production_queue
from controllers.sample_controller import list_samples
from views import (
    monitoring_view,
    order_approval_view,
    order_view,
    production_view,
    sample_view,
    shipment_view,
)

MENU_ACTIONS = {
    "1": sample_view.run,
    "2": order_view.run,
    "3": order_approval_view.run,
    "4": monitoring_view.run,
    "5": production_view.run,
    "6": shipment_view.run,
}


def _print_header():
    samples = list_samples()
    orders = list_orders()
    queue = get_production_queue()
    total_stock = sum(s.stock for s in samples)

    print("=" * 60)
    print("  반도체 시료 생산주문관리 시스템")
    print("=" * 60)
    print(f"시스템 현황   {datetime.now():%Y-%m-%d %H:%M:%S}")
    print(f"등록 시료 {len(samples)}종     총 재고 {total_stock} ea")
    print(f"전체 주문 {len(orders)}건     생산라인 {len(queue)}건 대기")
    print("-" * 60)


def _print_menu():
    print("[1] 시료 관리        [2] 시료 주문")
    print("[3] 주문 승인/거절   [4] 모니터링")
    print("[5] 생산라인 조회    [6] 출고 처리")
    print("[0] 종료")
    print("-" * 60)


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stdin.reconfigure(encoding="utf-8")

    while True:
        _print_header()
        _print_menu()
        choice = input("선택 > ").strip()

        if choice == "0":
            print("종료합니다.")
            return

        action = MENU_ACTIONS.get(choice)
        if action:
            action()
        else:
            print("잘못된 선택입니다.")


if __name__ == "__main__":
    main()
