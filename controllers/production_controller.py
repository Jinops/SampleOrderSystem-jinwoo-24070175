from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path

from models.enums import OrderStatus
from models.order import DEFAULT_DATA_DIR, Order
from models.order import list_orders as _list_orders
from models.order import save_order
from models.sample import get_sample, save_sample


@dataclass
class ProductionStatus:
    order: Order
    total_time: float
    progress_pct: float
    estimated_completion: datetime


def _production_queue(data_dir: Path) -> list[Order]:
    orders = [o for o in _list_orders(data_dir=data_dir) if o.status == OrderStatus.PRODUCING]
    return sorted(orders, key=lambda o: o.created_at)


def get_production_queue(data_dir: Path = DEFAULT_DATA_DIR) -> list[ProductionStatus]:
    queue = _production_queue(data_dir)
    result = []
    cumulative_eta = None

    for i, order in enumerate(queue):
        sample = get_sample(order.sample_id, data_dir=data_dir)
        total_time = sample.avg_process_time * order.actual_qty

        if i == 0:
            if order.production_started_at is None:
                order.production_started_at = datetime.now()
                save_order(order, data_dir=data_dir)
            elapsed_minutes = (datetime.now() - order.production_started_at).total_seconds() / 60
            progress_pct = min(100.0, (elapsed_minutes / total_time * 100) if total_time > 0 else 100.0)
            eta = order.production_started_at + timedelta(minutes=total_time)
        else:
            progress_pct = 0.0
            eta = cumulative_eta + timedelta(minutes=total_time)

        cumulative_eta = eta
        result.append(
            ProductionStatus(order=order, total_time=total_time, progress_pct=progress_pct, estimated_completion=eta)
        )

    return result


def complete_current_production(data_dir: Path = DEFAULT_DATA_DIR) -> Order:
    queue = _production_queue(data_dir)
    if not queue:
        raise ValueError("생산 중인 주문이 없습니다.")

    order = queue[0]
    if order.production_started_at is None:
        raise ValueError("아직 생산이 시작되지 않았습니다. 먼저 생산라인 조회로 큐를 확인하세요.")

    sample = get_sample(order.sample_id, data_dir=data_dir)
    total_time = sample.avg_process_time * order.actual_qty
    elapsed_minutes = (datetime.now() - order.production_started_at).total_seconds() / 60
    if elapsed_minutes < total_time:
        remaining = total_time - elapsed_minutes
        raise ValueError(f"아직 생산이 완료되지 않았습니다. 약 {remaining:.1f}분 더 필요합니다.")

    sample.stock += order.actual_qty
    sample.stock -= order.quantity
    save_sample(sample, data_dir=data_dir)

    order.status = OrderStatus.CONFIRMED
    save_order(order, data_dir=data_dir)
    return order
