from pathlib import Path

from models.sample import DEFAULT_DATA_DIR, Sample, get_sample
from models.sample import list_samples as _list_samples
from models.sample import save_sample


def is_duplicate_sample_id(sample_id: str, data_dir: Path = DEFAULT_DATA_DIR) -> bool:
    return get_sample(sample_id, data_dir=data_dir) is not None


def register_sample(
    sample_id: str,
    name: str,
    avg_process_time: float,
    yield_rate: float,
    stock: int,
    data_dir: Path = DEFAULT_DATA_DIR,
) -> Sample:
    if is_duplicate_sample_id(sample_id, data_dir=data_dir):
        raise ValueError(f"이미 등록된 시료 ID입니다: {sample_id}")
    if not (0 < yield_rate <= 1):
        raise ValueError(f"수율은 0 초과 1 이하여야 합니다: {yield_rate}")

    sample = Sample(
        sample_id=sample_id,
        name=name,
        avg_process_time=avg_process_time,
        yield_rate=yield_rate,
        stock=stock,
    )
    save_sample(sample, data_dir=data_dir)
    return sample


def list_samples(data_dir: Path = DEFAULT_DATA_DIR) -> list[Sample]:
    return _list_samples(data_dir=data_dir)


def search_samples(keyword: str, data_dir: Path = DEFAULT_DATA_DIR) -> list[Sample]:
    return [
        s
        for s in _list_samples(data_dir=data_dir)
        if keyword in s.sample_id or keyword in s.name
    ]
