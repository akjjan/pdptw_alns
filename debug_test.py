from alns import LiLimParser, ALNS
from evaluator_layer import FeasibilityChecker
import copy

if __name__ == "__main__":
    test_instance = LiLimParser.parse(
        "./pdp_100/pdp_100/lc101.txt")

    test_alns = ALNS(test_instance)
    initial_solution = test_alns.generate_initial_solution()
    print("Initial Solution:")
    print(f"Cost: {test_alns.calculate_all_cost(initial_solution):.2f}")
    print(
        f"Feasible: {FeasibilityChecker.check_solution(initial_solution, test_instance)}")
    print('-----------------------------')

    solution1 = copy.deepcopy(initial_solution)

    ITER_NUM = 10
    for i in range(ITER_NUM):
        old_cost = test_alns.calculate_all_cost(solution1)
        solution1 = test_alns.iterate(solution1)
        new_cost = test_alns.calculate_all_cost(solution1)
        is_feasible = FeasibilityChecker.check_solution(
            solution1, test_instance)
        print(
            f"Iter {i}: cost {old_cost:.2f} -> {new_cost:.2f}, feasible={is_feasible}")

    print('-----------------------------')
    print(f"Final cost: {test_alns.calculate_all_cost(solution1):.2f}")
    print(
        f"Final feasible: {FeasibilityChecker.check_solution(solution1, test_instance)}")
