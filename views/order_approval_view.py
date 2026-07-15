from controllers.order_controller import approve_order, list_reserved_orders, reject_order
from views.formatting import colorize, print_table


def _print_reserved_orders(orders):
    headers = ["번호", "주문번호", "고객", "시료ID", "수량"]
    widths = [6, 22, 20, 10, 8]
    rows = [[i, o.order_id, o.customer_name, o.sample_id, o.quantity] for i, o in enumerate(orders, start=1)]
    print_table(headers, rows, widths)


def _handle_process():
    orders = list_reserved_orders()
    if not orders:
        print("승인 대기 중인 주문이 없습니다.")
        return

    _print_reserved_orders(orders)
    choice = input("승인/거절할 번호 > ").strip()
    if not choice.isdigit() or not (1 <= int(choice) <= len(orders)):
        print("잘못된 번호입니다.")
        return

    order = orders[int(choice) - 1]
    decision = input(f"{order.order_id} 승인하시겠습니까? [Y]승인 [N]거절 > ").strip().upper()

    if decision == "Y":
        result = approve_order(order.order_id)
        print(f"승인 완료. 상태: RESERVED -> {colorize(result.status.value, result.status.value)}")
    elif decision == "N":
        result = reject_order(order.order_id)
        print(f"거절 완료. 상태: RESERVED -> {colorize(result.status.value, result.status.value)}")
    else:
        print("Y 또는 N만 입력 가능합니다.")


def run():
    while True:
        print("\n<주문 승인/거절>")
        print("[1] 승인 대기 목록 처리   [0] 뒤로")
        choice = input("선택 > ").strip()

        if choice == "1":
            _handle_process()
        elif choice == "0":
            return
        else:
            print("잘못된 선택입니다.")
