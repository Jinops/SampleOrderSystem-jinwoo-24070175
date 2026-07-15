from controllers.monitoring_controller import classify_sample_stock, count_orders_by_status
from controllers.order_controller import approve_order, create_order, reject_order
from controllers.sample_controller import register_sample
from models.enums import OrderStatus


def test_상태별_주문_건수를_집계하고_REJECTED는_제외한다(tmp_path):
    register_sample("S-001", "실리콘 웨이퍼-8인치", 0.5, 0.92, 480, data_dir=tmp_path)

    reserved = create_order("S-001", "A고객", 50, data_dir=tmp_path)
    confirmed = create_order("S-001", "B고객", 50, data_dir=tmp_path)
    approve_order(confirmed.order_id, data_dir=tmp_path)
    rejected = create_order("S-001", "C고객", 50, data_dir=tmp_path)
    reject_order(rejected.order_id, data_dir=tmp_path)
    producing = create_order("S-001", "D고객", 1000, data_dir=tmp_path)
    approve_order(producing.order_id, data_dir=tmp_path)

    counts = count_orders_by_status(data_dir=tmp_path)

    assert counts[OrderStatus.RESERVED] == 1
    assert counts[OrderStatus.CONFIRMED] == 1
    assert counts[OrderStatus.PRODUCING] == 1
    assert counts.get(OrderStatus.RELEASE, 0) == 0
    assert OrderStatus.REJECTED not in counts


def test_재고가_0이면_고갈이다(tmp_path):
    register_sample("S-001", "실리콘 웨이퍼-8인치", 0.5, 0.92, 0, data_dir=tmp_path)

    result = classify_sample_stock(data_dir=tmp_path)

    assert result[0].level == "고갈"


def test_대기수량_합이_재고보다_많으면_부족이다(tmp_path):
    register_sample("S-001", "실리콘 웨이퍼-8인치", 0.5, 0.92, 100, data_dir=tmp_path)
    create_order("S-001", "A고객", 150, data_dir=tmp_path)  # RESERVED, 150 > 100

    result = classify_sample_stock(data_dir=tmp_path)

    assert result[0].level == "부족"


def test_대기수량_합이_재고_이하면_여유다(tmp_path):
    register_sample("S-001", "실리콘 웨이퍼-8인치", 0.5, 0.92, 480, data_dir=tmp_path)
    create_order("S-001", "A고객", 100, data_dir=tmp_path)  # RESERVED, 100 <= 480

    result = classify_sample_stock(data_dir=tmp_path)

    assert result[0].level == "여유"
