from alns import LiLimParser, ALNS
from evaluator_layer import FeasibilityChecker
import time
import copy


def green_text(text: str) -> str:
    return f"\033[92m{text}\033[0m"


def test(file_name):
    test_instance = LiLimParser.parse(f"{file_name}")
    test_alns = ALNS(test_instance)
    # 生成初始解
    initial_solution = test_alns.generate_initial_solution()
    solution1 = copy.deepcopy(initial_solution)
    time1 = time.time()
    ITER_NUM = 1000
    for _ in range(ITER_NUM):
        solution1 = test_alns.iterate(solution1)
    time2 = time.time()
    print(
        f"ALNS迭代{ITER_NUM}次耗时: {time2 - time1:.2f}秒，平均每次迭代耗时: {(time2 - time1) / ITER_NUM:.2f}秒")
    stats = test_alns.get_stats()
    print(
        f"Stats: iterations={stats['iterations']}, infeasible_rejected={stats['infeasible_rejected']}, "
        f"better_accepted={stats['better_accepted']}, worse_candidates={stats['worse_candidates']}, "
        f"worse_accepted={stats['worse_accepted']}")
    print(f"After {ITER_NUM} iterations:")
    print(
        f"{file_name}解是否可行: {FeasibilityChecker.check_solution(test_alns.best_feasible_solution_)}")
    print(test_alns.best_feasible_solution_)
    print(green_text('-----------------------------'))


if __name__ == "__main__":
    # 打开./pdp_100/pdp_100/目录下的所有txt文件，依次测试
    import os
    directory = "./pdp_100/pdp_100/"
    for filename in os.listdir(directory):
        if filename.endswith(".txt"):
            test(os.path.join(directory, filename))
