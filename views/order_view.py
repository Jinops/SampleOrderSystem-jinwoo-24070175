from controllers.order_controller import create_order
from controllers.sample_controller import is_duplicate_sample_id
from views.formatting import colorize


def _handle_create_order():
    sample_id = input("시료 ID 입력 (예시: S-001) > ").strip()
    if not is_duplicate_sample_id(sample_id):
        print(f"등록되지 않은 시료 ID입니다: {sample_id}")
        return

    customer_name = input("고객명 > ").strip()
    try:
        quantity = int(input("주문 수량 > ").strip())
    except ValueError:
        print("숫자 형식이 올바르지 않습니다.")
        return

    try:
        order = create_order(sample_id, customer_name, quantity)
    except ValueError as e:
        print(f"주문 생성 실패: {e}")
        return

    print("예약 접수 완료.")
    print(f"주문번호   {order.order_id}")
    print(f"현재 상태   {colorize(order.status.value, order.status.value)}")


def run():
    while True:
        print("\n<시료 주문>")
        print("[1] 신규 주문   [0] 뒤로")
        choice = input("선택 > ").strip()

        if choice == "1":
            _handle_create_order()
        elif choice == "0":
            return
        else:
            print("잘못된 선택입니다.")
