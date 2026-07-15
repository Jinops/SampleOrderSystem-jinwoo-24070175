from controllers.production_controller import complete_current_production, get_production_queue


def _progress_bar(pct, width=10):
    filled = int(pct / 100 * width)
    return "[" + "■" * filled + "□" * (width - filled) + f"] {pct:.0f}%"


def _handle_view_queue():
    queue = get_production_queue()
    if not queue:
        print("생산 중인 주문이 없습니다.")
        return

    front = queue[0]
    print(f"현재 처리 중: {front.order.order_id} (시료 {front.order.sample_id}, 실생산량 {front.order.actual_qty}ea)")
    print(f"{_progress_bar(front.progress_pct)}  완료 예정 {front.estimated_completion:%H:%M}")

    if len(queue) > 1:
        print("\n대기 중인 주문 (FIFO)")
        for s in queue[1:]:
            print(f"{s.order.order_id}  실생산량 {s.order.actual_qty}ea  예상 완료 {s.estimated_completion:%H:%M}")


def _handle_complete():
    try:
        order = complete_current_production()
        print(f"생산 완료 처리됨: {order.order_id} -> {order.status.value}")
    except ValueError as e:
        print(f"처리 실패: {e}")


def run():
    while True:
        print("\n[5] 생산라인 조회")
        print("[1] 큐 조회   [2] 생산완료 처리   [0] 뒤로")
        choice = input("선택 > ").strip()

        if choice == "1":
            _handle_view_queue()
        elif choice == "2":
            _handle_complete()
        elif choice == "0":
            return
        else:
            print("잘못된 선택입니다.")
