from datetime import datetime
from math import ceil
from pathlib import Path

from models.enums import OrderStatus
from models.order import DEFAULT_DATA_DIR, Order, get_order
from models.order import list_orders as _list_orders
from models.order import save_order
from models.sample import get_sample, save_sample


def _generate_order_id(created_at: datetime, data_dir: Path) -> str:
    date_str = created_at.strftime("%Y%m%d")
    prefix = f"ORD-{date_str}-"
    same_day_count = sum(1 for o in _list_orders(data_dir=data_dir) if o.order_id.startswith(prefix))
    return f"{prefix}{same_day_count + 1:04d}"


def create_order(
    sample_id: str,
    customer_name: str,
    quantity: int,
    data_dir: Path = DEFAULT_DATA_DIR,
) -> Order:
    if get_sample(sample_id, data_dir=data_dir) is None:
        raise ValueError(f"등록되지 않은 시료 ID입니다: {sample_id}")
    if quantity < 1:
        raise ValueError(f"주문 수량은 1 이상이어야 합니다: {quantity}")

    created_at = datetime.now()
    order = Order(
        order_id=_generate_order_id(created_at, data_dir),
        sample_id=sample_id,
        customer_name=customer_name,
        quantity=quantity,
        created_at=created_at,
    )
    save_order(order, data_dir=data_dir)
    return order


def list_orders(data_dir: Path = DEFAULT_DATA_DIR) -> list[Order]:
    return _list_orders(data_dir=data_dir)


def list_reserved_orders(data_dir: Path = DEFAULT_DATA_DIR) -> list[Order]:
    return [o for o in _list_orders(data_dir=data_dir) if o.status == OrderStatus.RESERVED]


def _require_reserved_order(order_id: str, data_dir: Path) -> Order:
    order = get_order(order_id, data_dir=data_dir)
    if order is None:
        raise ValueError(f"존재하지 않는 주문번호입니다: {order_id}")
    if order.status != OrderStatus.RESERVED:
        raise ValueError(f"RESERVED 상태의 주문만 처리할 수 있습니다: {order_id} ({order.status.value})")
    return order


def approve_order(order_id: str, data_dir: Path = DEFAULT_DATA_DIR) -> Order:
    order = _require_reserved_order(order_id, data_dir)
    sample = get_sample(order.sample_id, data_dir=data_dir)

    if sample.stock >= order.quantity:
        sample.stock -= order.quantity
        save_sample(sample, data_dir=data_dir)
        order.status = OrderStatus.CONFIRMED
    else:
        shortage = order.quantity - sample.stock
        order.shortage = shortage
        order.actual_qty = ceil(shortage / sample.yield_rate)
        order.status = OrderStatus.PRODUCING

    save_order(order, data_dir=data_dir)
    return order


def reject_order(order_id: str, data_dir: Path = DEFAULT_DATA_DIR) -> Order:
    order = _require_reserved_order(order_id, data_dir)
    order.status = OrderStatus.REJECTED
    save_order(order, data_dir=data_dir)
    return order
