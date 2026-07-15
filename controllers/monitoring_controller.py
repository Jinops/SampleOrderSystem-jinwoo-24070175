from dataclasses import dataclass
from pathlib import Path

from models.enums import OrderStatus
from models.order import DEFAULT_DATA_DIR
from models.order import list_orders as _list_orders
from models.sample import Sample
from models.sample import list_samples as _list_samples

PENDING_STATUSES = (OrderStatus.RESERVED, OrderStatus.PRODUCING)


def count_orders_by_status(data_dir: Path = DEFAULT_DATA_DIR) -> dict:
    counts: dict = {}
    for order in _list_orders(data_dir=data_dir):
        if order.status == OrderStatus.REJECTED:
            continue
        counts[order.status] = counts.get(order.status, 0) + 1
    return counts


@dataclass
class StockStatus:
    sample: Sample
    pending_quantity: int
    level: str


def classify_sample_stock(data_dir: Path = DEFAULT_DATA_DIR) -> list[StockStatus]:
    orders = _list_orders(data_dir=data_dir)
    result = []
    for sample in _list_samples(data_dir=data_dir):
        pending_quantity = sum(
            o.quantity
            for o in orders
            if o.sample_id == sample.sample_id and o.status in PENDING_STATUSES
        )
        if sample.stock == 0:
            level = "고갈"
        elif pending_quantity > sample.stock:
            level = "부족"
        else:
            level = "여유"
        result.append(StockStatus(sample=sample, pending_quantity=pending_quantity, level=level))
    return result
