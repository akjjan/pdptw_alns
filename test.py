from alns import LiLimParser, ALNS
from evaluator_layer import FeasibilityChecker
from solution_layer import Solution
import time
import copy
if __name__ == "__main__":
    test_instance = LiLimParser.parse(
        "./pdp_100/pdp_100/lc101.txt")

    test_alns = ALNS(test_instance)
    initial_solution = test_alns.generate_initial_solution()
    print("Initial Solution:")
    print("Routes:", initial_solution.routes_)
    print("Request Bank:", initial_solution.request_bank_)
    print("Solution Cost:", initial_solution.solution_cost_)
    print("Vehicle Count:", initial_solution.vehicle_count_)
    print('-----------------------------')
    solution1 = copy.deepcopy(initial_solution)
    time1 = time.time()
    ITER_NUM = 100
    for _ in range(ITER_NUM):
        solution1 = test_alns.iterate(solution1)
    time2 = time.time()
    print(
        f"ALNS迭代{ITER_NUM}次耗时: {time2 - time1:.4f}秒，平均每次迭代耗时: {(time2 - time1) / ITER_NUM:.4f}秒")
    for route in solution1.routes_:
        assert FeasibilityChecker.is_valid_route(
            route, test_instance), f"Route {route} 违反起终点、偶数约束"
    print(f"After {ITER_NUM} iterations:")
    print(
        f"解是否可行: {FeasibilityChecker.check_solution(solution1, test_instance)}")
    print("Routes:", solution1.routes_)
    print("Request Bank:", solution1.request_bank_)
    print("Solution Cost:", solution1.solution_cost_)
    print("Vehicle Count:", solution1.vehicle_count_)
