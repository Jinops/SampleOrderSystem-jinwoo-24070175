import pytest

from controllers.sample_controller import list_samples, register_sample, search_samples


def test_정상_등록하면_목록에서_조회된다(tmp_path):
    register_sample("S-001", "실리콘 웨이퍼-8인치", 0.5, 0.92, 480, data_dir=tmp_path)

    samples = list_samples(data_dir=tmp_path)

    assert len(samples) == 1
    assert samples[0].sample_id == "S-001"
    assert samples[0].stock == 480


def test_중복된_ID로_등록하면_에러(tmp_path):
    register_sample("S-001", "실리콘 웨이퍼-8인치", 0.5, 0.92, 480, data_dir=tmp_path)

    with pytest.raises(ValueError):
        register_sample("S-001", "다른 이름", 0.3, 0.8, 100, data_dir=tmp_path)


@pytest.mark.parametrize("yield_rate", [0, -0.1, 1.1])
def test_수율이_0_초과_1_이하_범위를_벗어나면_에러(tmp_path, yield_rate):
    with pytest.raises(ValueError):
        register_sample("S-001", "실리콘 웨이퍼-8인치", 0.5, yield_rate, 480, data_dir=tmp_path)


def test_이름으로_검색할_수_있다(tmp_path):
    register_sample("S-001", "실리콘 웨이퍼-8인치", 0.5, 0.92, 480, data_dir=tmp_path)
    register_sample("S-002", "GaN 에피택셜-4인치", 0.3, 0.78, 220, data_dir=tmp_path)

    result = search_samples("웨이퍼", data_dir=tmp_path)

    assert [s.sample_id for s in result] == ["S-001"]


def test_ID로도_검색할_수_있다(tmp_path):
    register_sample("S-001", "실리콘 웨이퍼-8인치", 0.5, 0.92, 480, data_dir=tmp_path)
    register_sample("S-002", "GaN 에피택셜-4인치", 0.3, 0.78, 220, data_dir=tmp_path)

    result = search_samples("S-002", data_dir=tmp_path)

    assert [s.sample_id for s in result] == ["S-002"]
