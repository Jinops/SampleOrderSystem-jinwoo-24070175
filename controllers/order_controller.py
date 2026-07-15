from datetime import datetime
from pathlib import Path

from models.order import DEFAULT_DATA_DIR, Order
from models.order import list_orders as _list_orders
from models.order import save_order
from models.sample import get_sample


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
