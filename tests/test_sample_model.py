from models.sample import Sample, get_sample, list_samples, save_sample


def test_새_시료를_저장하면_목록에서_조회된다(tmp_path):
    sample = Sample(sample_id="S-001", name="실리콘 웨이퍼-8인치", avg_process_time=0.5, yield_rate=0.92, stock=480)

    save_sample(sample, data_dir=tmp_path)

    samples = list_samples(data_dir=tmp_path)
    assert samples == [sample]


def test_시료_ID로_단건_조회할_수_있다(tmp_path):
    sample = Sample(sample_id="S-001", name="실리콘 웨이퍼-8인치", avg_process_time=0.5, yield_rate=0.92, stock=480)
    save_sample(sample, data_dir=tmp_path)

    found = get_sample("S-001", data_dir=tmp_path)

    assert found == sample


def test_존재하지_않는_ID_조회시_None을_반환한다(tmp_path):
    assert get_sample("NOPE", data_dir=tmp_path) is None


def test_동일_ID로_다시_저장하면_기존_값이_갱신된다(tmp_path):
    sample = Sample(sample_id="S-001", name="실리콘 웨이퍼-8인치", avg_process_time=0.5, yield_rate=0.92, stock=480)
    save_sample(sample, data_dir=tmp_path)

    updated = Sample(sample_id="S-001", name="실리콘 웨이퍼-8인치", avg_process_time=0.5, yield_rate=0.92, stock=300)
    save_sample(updated, data_dir=tmp_path)

    samples = list_samples(data_dir=tmp_path)
    assert samples == [updated]


def test_파일이_없으면_빈_목록을_반환한다(tmp_path):
    assert list_samples(data_dir=tmp_path) == []
