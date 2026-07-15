from controllers.monitoring_controller import classify_sample_stock, count_orders_by_status
from views.formatting import colorize, print_table


def _handle_order_counts():
    counts = count_orders_by_status()
    if not counts:
        print("집계할 주문이 없습니다.")
        return
    headers = ["상태", "건수"]
    widths = [12, 6]
    rows = [[colorize(status.value, status.value), count] for status, count in counts.items()]
    print_table(headers, rows, widths)


def _handle_stock_status():
    statuses = classify_sample_stock()
    if not statuses:
        print("등록된 시료가 없습니다.")
        return
    headers = ["시료명", "재고", "대기수량", "상태"]
    widths = [20, 8, 10, 10]
    rows = [
        [s.sample.name, s.sample.stock, s.pending_quantity, colorize(s.level, s.level)]
        for s in statuses
    ]
    print_table(headers, rows, widths)


def run():
    while True:
        print("\n[4] 모니터링")
        print("[1] 주문량 확인   [2] 재고량 확인   [0] 뒤로")
        choice = input("선택 > ").strip()

        if choice == "1":
            _handle_order_counts()
        elif choice == "2":
            _handle_stock_status()
        elif choice == "0":
            return
        else:
            print("잘못된 선택입니다.")
