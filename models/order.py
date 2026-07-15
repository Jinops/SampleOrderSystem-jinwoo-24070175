import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

from models.enums import OrderStatus

DEFAULT_DATA_DIR = Path(__file__).resolve().parent.parent / "data"
ORDERS_FILE = "orders.json"


@dataclass
class Order:
    order_id: str
    sample_id: str
    customer_name: str
    quantity: int
    status: OrderStatus = OrderStatus.RESERVED
    created_at: datetime = field(default_factory=datetime.now)
    shortage: int | None = None
    actual_qty: int | None = None
    production_started_at: datetime | None = None


def _orders_path(data_dir: Path = DEFAULT_DATA_DIR) -> Path:
    return data_dir / ORDERS_FILE


def _to_dict(order: Order) -> dict:
    return {
        "order_id": order.order_id,
        "sample_id": order.sample_id,
        "customer_name": order.customer_name,
        "quantity": order.quantity,
        "status": order.status.value,
        "created_at": order.created_at.isoformat(),
        "shortage": order.shortage,
        "actual_qty": order.actual_qty,
        "production_started_at": (
            order.production_started_at.isoformat() if order.production_started_at else None
        ),
    }


def _from_dict(data: dict) -> Order:
    return Order(
        order_id=data["order_id"],
        sample_id=data["sample_id"],
        customer_name=data["customer_name"],
        quantity=data["quantity"],
        status=OrderStatus(data["status"]),
        created_at=datetime.fromisoformat(data["created_at"]),
        shortage=data.get("shortage"),
        actual_qty=data.get("actual_qty"),
        production_started_at=(
            datetime.fromisoformat(data["production_started_at"])
            if data.get("production_started_at")
            else None
        ),
    )


def list_orders(data_dir: Path = DEFAULT_DATA_DIR) -> list[Order]:
    path = _orders_path(data_dir)
    if not path.exists():
        return []
    with open(path, encoding="utf-8") as f:
        raw = json.load(f)
    return [_from_dict(item) for item in raw]


def get_order(order_id: str, data_dir: Path = DEFAULT_DATA_DIR) -> Order | None:
    for order in list_orders(data_dir):
        if order.order_id == order_id:
            return order
    return None


def save_order(order: Order, data_dir: Path = DEFAULT_DATA_DIR) -> None:
    orders = [o for o in list_orders(data_dir) if o.order_id != order.order_id]
    orders.append(order)
    data_dir.mkdir(parents=True, exist_ok=True)
    with open(_orders_path(data_dir), "w", encoding="utf-8") as f:
        json.dump([_to_dict(o) for o in orders], f, ensure_ascii=False, indent=2)
