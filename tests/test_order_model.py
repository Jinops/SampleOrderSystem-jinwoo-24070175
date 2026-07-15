from datetime import datetime

from models.enums import OrderStatus
from models.order import Order, get_order, list_orders, save_order


def _make_order(**overrides):
    defaults = dict(
        order_id="ORD-0001",
        sample_id="S-001",
        customer_name="삼성전자 파운드리",
        quantity=200,
        status=OrderStatus.RESERVED,
        created_at=datetime(2026, 4, 16, 9, 32, 15),
    )
    defaults.update(overrides)
    return Order(**defaults)


def test_새_주문을_저장하면_목록에서_조회된다(tmp_path):
    order = _make_order()

    save_order(order, data_dir=tmp_path)

    assert list_orders(data_dir=tmp_path) == [order]


def test_주문번호로_단건_조회할_수_있다(tmp_path):
    order = _make_order()
    save_order(order, data_dir=tmp_path)

    found = get_order("ORD-0001", data_dir=tmp_path)

    assert found == order


def test_존재하지_않는_주문번호_조회시_None을_반환한다(tmp_path):
    assert get_order("NOPE", data_dir=tmp_path) is None


def test_status와_created_at이_직렬화_역직렬화되어도_동일하다(tmp_path):
    order = _make_order(status=OrderStatus.PRODUCING)
    save_order(order, data_dir=tmp_path)

    found = get_order("ORD-0001", data_dir=tmp_path)

    assert found.status == OrderStatus.PRODUCING
    assert found.created_at == datetime(2026, 4, 16, 9, 32, 15)


def test_동일_주문번호로_다시_저장하면_상태가_갱신된다(tmp_path):
    order = _make_order(status=OrderStatus.RESERVED)
    save_order(order, data_dir=tmp_path)

    updated = _make_order(status=OrderStatus.CONFIRMED)
    save_order(updated, data_dir=tmp_path)

    orders = list_orders(data_dir=tmp_path)
    assert orders == [updated]


def test_파일이_없으면_빈_목록을_반환한다(tmp_path):
    assert list_orders(data_dir=tmp_path) == []


def test_shortage_actual_qty_production_started_at_기본값은_None이다(tmp_path):
    order = _make_order()

    assert order.shortage is None
    assert order.actual_qty is None
    assert order.production_started_at is None


def test_생산_관련_필드가_저장_후_복원되어도_동일하다(tmp_path):
    order = _make_order(
        status=OrderStatus.PRODUCING,
        shortage=120,
        actual_qty=131,
        production_started_at=datetime(2026, 4, 16, 10, 0, 0),
    )
    save_order(order, data_dir=tmp_path)

    found = get_order("ORD-0001", data_dir=tmp_path)

    assert found.shortage == 120
    assert found.actual_qty == 131
    assert found.production_started_at == datetime(2026, 4, 16, 10, 0, 0)
