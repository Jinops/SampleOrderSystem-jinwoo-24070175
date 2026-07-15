from controllers.monitoring_controller import classify_sample_stock, count_orders_by_status


def _handle_order_counts():
    counts = count_orders_by_status()
    if not counts:
        print("집계할 주문이 없습니다.")
        return
    print(f"{'상태':<12}{'건수':<6}")
    for status, count in counts.items():
        print(f"{status.value:<12}{count:<6}")


def _handle_stock_status():
    statuses = classify_sample_stock()
    if not statuses:
        print("등록된 시료가 없습니다.")
        return
    print(f"{'시료명':<20}{'재고':<8}{'대기수량':<10}{'상태':<6}")
    for s in statuses:
        print(f"{s.sample.name:<20}{s.sample.stock:<8}{s.pending_quantity:<10}{s.level:<6}")


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
