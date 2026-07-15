from pathlib import Path

from models.enums import OrderStatus
from models.order import DEFAULT_DATA_DIR, Order, get_order
from models.order import list_orders as _list_orders
from models.order import save_order


def list_confirmed_orders(data_dir: Path = DEFAULT_DATA_DIR) -> list[Order]:
    return [o for o in _list_orders(data_dir=data_dir) if o.status == OrderStatus.CONFIRMED]


def ship_order(order_id: str, data_dir: Path = DEFAULT_DATA_DIR) -> Order:
    order = get_order(order_id, data_dir=data_dir)
    if order is None:
        raise ValueError(f"존재하지 않는 주문번호입니다: {order_id}")
    if order.status != OrderStatus.CONFIRMED:
        raise ValueError(f"CONFIRMED 상태의 주문만 출고할 수 있습니다: {order_id} ({order.status.value})")

    order.status = OrderStatus.RELEASE
    save_order(order, data_dir=data_dir)
    return order
