import pytest

from controllers.order_controller import approve_order, create_order, reject_order
from controllers.sample_controller import register_sample
from models.enums import OrderStatus
from models.sample import get_sample


def _setup(tmp_path, stock):
    register_sample("S-001", "실리콘 웨이퍼-8인치", 0.5, 0.92, stock, data_dir=tmp_path)
    return create_order("S-001", "삼성전자 파운드리", 200, data_dir=tmp_path)


def test_재고가_충분하면_승인시_CONFIRMED로_전환되고_재고가_차감된다(tmp_path):
    order = _setup(tmp_path, stock=480)

    approved = approve_order(order.order_id, data_dir=tmp_path)

    assert approved.status == OrderStatus.CONFIRMED
    assert get_sample("S-001", data_dir=tmp_path).stock == 280


def test_재고가_부족하면_승인시_PRODUCING으로_전환되고_재고는_그대로다(tmp_path):
    order = _setup(tmp_path, stock=50)

    approved = approve_order(order.order_id, data_dir=tmp_path)

    assert approved.status == OrderStatus.PRODUCING
    assert get_sample("S-001", data_dir=tmp_path).stock == 50


def test_거절하면_REJECTED로_전환된다(tmp_path):
    order = _setup(tmp_path, stock=480)

    rejected = reject_order(order.order_id, data_dir=tmp_path)

    assert rejected.status == OrderStatus.REJECTED


def test_RESERVED가_아닌_주문을_승인하면_에러(tmp_path):
    order = _setup(tmp_path, stock=480)
    reject_order(order.order_id, data_dir=tmp_path)

    with pytest.raises(ValueError):
        approve_order(order.order_id, data_dir=tmp_path)


def test_RESERVED가_아닌_주문을_거절하면_에러(tmp_path):
    order = _setup(tmp_path, stock=480)
    approve_order(order.order_id, data_dir=tmp_path)

    with pytest.raises(ValueError):
        reject_order(order.order_id, data_dir=tmp_path)
