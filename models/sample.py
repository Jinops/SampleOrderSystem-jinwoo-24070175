import json
from dataclasses import asdict, dataclass
from pathlib import Path

DEFAULT_DATA_DIR = Path(__file__).resolve().parent.parent / "data"
SAMPLES_FILE = "samples.json"


@dataclass
class Sample:
    sample_id: str
    name: str
    avg_process_time: float
    yield_rate: float
    stock: int


def _samples_path(data_dir: Path = DEFAULT_DATA_DIR) -> Path:
    return data_dir / SAMPLES_FILE


def list_samples(data_dir: Path = DEFAULT_DATA_DIR) -> list[Sample]:
    path = _samples_path(data_dir)
    if not path.exists():
        return []
    with open(path, encoding="utf-8") as f:
        raw = json.load(f)
    return [Sample(**item) for item in raw]


def get_sample(sample_id: str, data_dir: Path = DEFAULT_DATA_DIR) -> Sample | None:
    for sample in list_samples(data_dir):
        if sample.sample_id == sample_id:
            return sample
    return None


def save_sample(sample: Sample, data_dir: Path = DEFAULT_DATA_DIR) -> None:
    samples = [s for s in list_samples(data_dir) if s.sample_id != sample.sample_id]
    samples.append(sample)
    data_dir.mkdir(parents=True, exist_ok=True)
    with open(_samples_path(data_dir), "w", encoding="utf-8") as f:
        json.dump([asdict(s) for s in samples], f, ensure_ascii=False, indent=2)


def search_samples(keyword: str, data_dir: Path = DEFAULT_DATA_DIR) -> list[Sample]:
    return [s for s in list_samples(data_dir) if keyword in s.name]
