import pytest

from controllers.order_controller import approve_order, create_order
from controllers.sample_controller import register_sample
from controllers.shipment_controller import list_confirmed_orders, ship_order
from models.enums import OrderStatus


def _confirmed_order(tmp_path, customer_name="A고객", quantity=100):
    register_sample("S-001", "실리콘 웨이퍼-8인치", 0.5, 0.92, 480, data_dir=tmp_path)
    order = create_order("S-001", customer_name, quantity, data_dir=tmp_path)
    return approve_order(order.order_id, data_dir=tmp_path)


def test_CONFIRMED_주문만_목록에_조회된다(tmp_path):
    confirmed = _confirmed_order(tmp_path)

    result = list_confirmed_orders(data_dir=tmp_path)

    assert [o.order_id for o in result] == [confirmed.order_id]


def test_출고처리하면_RELEASE로_전환된다(tmp_path):
    confirmed = _confirmed_order(tmp_path)

    shipped = ship_order(confirmed.order_id, data_dir=tmp_path)

    assert shipped.status == OrderStatus.RELEASE


def test_CONFIRMED가_아닌_주문을_출고하면_에러(tmp_path):
    register_sample("S-001", "실리콘 웨이퍼-8인치", 0.5, 0.92, 480, data_dir=tmp_path)
    reserved = create_order("S-001", "A고객", 100, data_dir=tmp_path)

    with pytest.raises(ValueError):
        ship_order(reserved.order_id, data_dir=tmp_path)
