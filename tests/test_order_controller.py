import re

import pytest

from controllers.order_controller import create_order
from controllers.sample_controller import register_sample
from models.enums import OrderStatus


def _register_default_sample(tmp_path):
    register_sample("S-001", "실리콘 웨이퍼-8인치", 0.5, 0.92, 480, data_dir=tmp_path)


def test_주문을_생성하면_RESERVED_상태로_저장된다(tmp_path):
    _register_default_sample(tmp_path)

    order = create_order("S-001", "삼성전자 파운드리", 200, data_dir=tmp_path)

    assert order.status == OrderStatus.RESERVED
    assert order.sample_id == "S-001"
    assert order.customer_name == "삼성전자 파운드리"
    assert order.quantity == 200


def test_주문번호는_ORD_날짜_순번_형식이다(tmp_path):
    _register_default_sample(tmp_path)

    order = create_order("S-001", "삼성전자 파운드리", 200, data_dir=tmp_path)

    assert re.match(r"^ORD-\d{8}-\d{4}$", order.order_id)


def test_같은_날_두번째_주문은_순번이_증가한다(tmp_path):
    _register_default_sample(tmp_path)

    first = create_order("S-001", "삼성전자 파운드리", 200, data_dir=tmp_path)
    second = create_order("S-001", "SK하이닉스", 150, data_dir=tmp_path)

    first_seq = int(first.order_id.split("-")[-1])
    second_seq = int(second.order_id.split("-")[-1])
    assert second_seq == first_seq + 1


def test_존재하지_않는_시료로_주문하면_에러(tmp_path):
    with pytest.raises(ValueError):
        create_order("NOPE", "삼성전자 파운드리", 200, data_dir=tmp_path)


@pytest.mark.parametrize("quantity", [0, -5])
def test_수량이_1보다_작으면_에러(tmp_path, quantity):
    _register_default_sample(tmp_path)

    with pytest.raises(ValueError):
        create_order("S-001", "삼성전자 파운드리", quantity, data_dir=tmp_path)
