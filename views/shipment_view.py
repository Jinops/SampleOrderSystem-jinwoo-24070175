from controllers.shipment_controller import list_confirmed_orders, ship_order


def _print_confirmed_orders(orders):
    print(f"{'번호':<6}{'주문번호':<22}{'고객':<20}{'시료ID':<10}{'수량':<8}")
    for i, o in enumerate(orders, start=1):
        print(f"{i:<6}{o.order_id:<22}{o.customer_name:<20}{o.sample_id:<10}{o.quantity:<8}")


def _handle_ship():
    orders = list_confirmed_orders()
    if not orders:
        print("출고 가능한 주문이 없습니다.")
        return

    _print_confirmed_orders(orders)
    choice = input("출고할 번호 > ").strip()
    if not choice.isdigit() or not (1 <= int(choice) <= len(orders)):
        print("잘못된 번호입니다.")
        return

    order = orders[int(choice) - 1]
    shipped = ship_order(order.order_id)
    print(f"출고 처리 완료. 상태: CONFIRMED -> {shipped.status.value}")


def run():
    while True:
        print("\n[6] 출고 처리")
        print("[1] 출고 가능 목록   [0] 뒤로")
        choice = input("선택 > ").strip()

        if choice == "1":
            _handle_ship()
        elif choice == "0":
            return
        else:
            print("잘못된 선택입니다.")
