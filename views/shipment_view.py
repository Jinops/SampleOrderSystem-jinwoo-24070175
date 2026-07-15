from controllers.shipment_controller import list_confirmed_orders, ship_order
from views.formatting import colorize, print_table


def _print_confirmed_orders(orders):
    headers = ["번호", "주문번호", "고객", "시료ID", "수량"]
    widths = [6, 22, 20, 10, 8]
    rows = [[i, o.order_id, o.customer_name, o.sample_id, o.quantity] for i, o in enumerate(orders, start=1)]
    print_table(headers, rows, widths)


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
    print(f"출고 처리 완료. 상태: CONFIRMED -> {colorize(shipped.status.value, shipped.status.value)}")


def run():
    while True:
        print("\n<출고 처리>")
        print("[1] 출고 가능 목록   [0] 뒤로")
        choice = input("선택 > ").strip()

        if choice == "1":
            _handle_ship()
        elif choice == "0":
            return
        else:
            print("잘못된 선택입니다.")
