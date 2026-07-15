from controllers.sample_controller import list_samples, register_sample, search_samples


def _print_samples(samples):
    if not samples:
        print("등록된 시료가 없습니다.")
        return
    print(f"{'ID':<8}{'시료명':<20}{'평균 생산시간':<14}{'수율':<8}{'재고':<8}")
    for s in samples:
        print(f"{s.sample_id:<8}{s.name:<20}{s.avg_process_time:<14}{s.yield_rate:<8}{s.stock:<8}")


def _handle_register():
    sample_id = input("시료 ID > ").strip()
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
    keyword = input("검색어 > ").strip()
    _print_samples(search_samples(keyword))


def run():
    while True:
        print("\n[1] 시료 관리")
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
