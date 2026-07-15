import pytest

from controllers.order_controller import approve_order, create_order
from controllers.production_controller import complete_current_production, get_production_queue
from controllers.sample_controller import register_sample
from models.enums import OrderStatus
from models.sample import get_sample


def test_생산큐는_PRODUCING_주문만_created_at_순서로_반환한다(tmp_path):
    register_sample("S-001", "실리콘 웨이퍼-8인치", 0.5, 0.92, 50, data_dir=tmp_path)
    first = approve_order(create_order("S-001", "A고객", 200, data_dir=tmp_path).order_id, data_dir=tmp_path)
    second = approve_order(create_order("S-001", "B고객", 300, data_dir=tmp_path).order_id, data_dir=tmp_path)

    queue = get_production_queue(data_dir=tmp_path)

    assert [s.order.order_id for s in queue] == [first.order_id, second.order_id]


def test_맨_앞_주문의_진행률은_0에서_100_사이다(tmp_path):
    register_sample("S-001", "실리콘 웨이퍼-8인치", 0.5, 0.92, 50, data_dir=tmp_path)
    approve_order(create_order("S-001", "A고객", 200, data_dir=tmp_path).order_id, data_dir=tmp_path)

    queue = get_production_queue(data_dir=tmp_path)

    assert 0 <= queue[0].progress_pct <= 100


def test_생산완료_처리시_재고가_증가후_차감되고_CONFIRMED로_전환된다(tmp_path):
    register_sample("S-001", "실리콘 웨이퍼-8인치", 0.5, 0.92, 50, data_dir=tmp_path)
    order = approve_order(create_order("S-001", "A고객", 200, data_dir=tmp_path).order_id, data_dir=tmp_path)
    # shortage=150, actual_qty=ceil(150/0.92)=164 -> stock: 50 + 164 - 200 = 14

    completed = complete_current_production(data_dir=tmp_path)

    assert completed.order_id == order.order_id
    assert completed.status == OrderStatus.CONFIRMED
    assert get_sample("S-001", data_dir=tmp_path).stock == 14


def test_생산_중인_주문이_없으면_완료처리시_에러(tmp_path):
    register_sample("S-001", "실리콘 웨이퍼-8인치", 0.5, 0.92, 480, data_dir=tmp_path)

    with pytest.raises(ValueError):
        complete_current_production(data_dir=tmp_path)
