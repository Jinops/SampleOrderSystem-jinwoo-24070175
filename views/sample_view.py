from controllers.sample_controller import (
    is_duplicate_sample_id,
    list_samples,
    register_sample,
    search_samples,
)
from views.formatting import print_section_header, print_table


def _print_samples(samples):
    if not samples:
        print("등록된 시료가 없습니다.")
        return
    headers = ["ID", "시료명", "평균 생산시간", "수율", "재고"]
    widths = [8, 20, 14, 8, 8]
    rows = [[s.sample_id, s.name, s.avg_process_time, s.yield_rate, s.stock] for s in samples]
    print_table(headers, rows, widths)


def _handle_register():
    sample_id = input("시료 ID 입력 (예시: S-001) > ").strip()
    if is_duplicate_sample_id(sample_id):
        print(f"이미 등록된 시료 ID입니다: {sample_id}")
        return

    name = input("시료명 > ").strip()
    try:
        avg_process_time = float(input("평균 생산시간(분) > ").strip())
        yield_rate = float(input("수율(0~1) > ").strip())
        stock = int(input("초기 재고 > ").strip())
    except ValueError:
        print("숫자 형식이 올바르지 않습니다.")
        return

    try:
        register_sample(sample_id, name, avg_process_time, yield_rate, stock)
        print("등록 완료.")
    except ValueError as e:
        print(f"등록 실패: {e}")


def _handle_list():
    _print_samples(list_samples())


def _handle_search():
    keyword = input("검색어 (ID 또는 시료명) > ").strip()
    _print_samples(search_samples(keyword))


def run():
    while True:
        print_section_header("시료 관리")
        print("[1] 시료 등록   [2] 시료 목록   [3] 시료 검색   [0] 뒤로")
        choice = input("선택 > ").strip()

        if choice == "1":
            _handle_register()
        elif choice == "2":
            _handle_list()
        elif choice == "3":
            _handle_search()
        elif choice == "0":
            return
        else:
            print("잘못된 선택입니다.")
