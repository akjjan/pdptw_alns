from alns import LiLimParser, ALNS
from evaluator_layer import FeasibilityChecker
from solution_layer import Solution
import time
import copy


def green_text(text: str) -> str:
    return f"\033[92m{text}\033[0m"


if __name__ == "__main__":
    test_instance = LiLimParser.parse(
        "./pdp_100/pdp_100/lc101.txt")

    test_alns = ALNS(test_instance)
    # 生成初始解
    initial_solution = test_alns.generate_initial_solution()
    print(green_text("Initial Solution:"))
    print(initial_solution)
    print('-----------------------------')

    solution1 = copy.deepcopy(initial_solution)

    time1 = time.time()

    ITER_NUM = 1000
    for _ in range(ITER_NUM):
        solution1 = test_alns.iterate(solution1)
    time2 = time.time()

    print(
        f"ALNS迭代{ITER_NUM}次耗时: {time2 - time1:.4f}秒，平均每次迭代耗时: {(time2 - time1) / ITER_NUM:.4f}秒")
    stats = test_alns.get_stats()
    print(
        f"Stats: iterations={stats['iterations']}, infeasible_rejected={stats['infeasible_rejected']}, "
        f"better_accepted={stats['better_accepted']}, worse_candidates={stats['worse_candidates']}, "
        f"worse_accepted={stats['worse_accepted']}")
    print(green_text(f"After {ITER_NUM} iterations:"))
    print(
        f"解是否可行: {FeasibilityChecker.check_solution(test_alns.best_feasible_solution, test_instance)}")
    print(test_alns.best_feasible_solution)
