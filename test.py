from alns import LiLimParser, ALNS
from evaluator_layer import FeasibilityChecker
from solution_layer import Solution

if __name__ == "__main__":
    test_instance = LiLimParser.parse(
        "./pdp_100/pdp_100/lc101.txt")

    test_alns = ALNS(test_instance)
    empty_solution = Solution.from_instance(test_instance)
    initial_solution = test_alns.iterate(empty_solution)
    print("Initial Solution:")
    print("Routes:", initial_solution.routes_)
    print("Request Bank:", initial_solution.request_bank_)
    print("Solution Cost:", initial_solution.solution_cost_)
    print("Vehicle Count:", initial_solution.vehicle_count_)
    print('-----------------------------')
    solution1 = initial_solution.copy()
    for _ in range(100):
        solution1 = test_alns.iterate(solution1)
    for route in solution1.routes_:
        assert FeasibilityChecker.is_valid_route(
            route, test_instance), f"Route {route} 违反起终点、偶数约束"
    print("After 100 iterations:")
    print("Routes:", solution1.routes_)
    print("Request Bank:", solution1.request_bank_)
    print("Solution Cost:", solution1.solution_cost_)
    print("Vehicle Count:", solution1.vehicle_count_)
