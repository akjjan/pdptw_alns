from alns import LiLimParser, ALNS
from solution_layer import Solution
if __name__ == "__main__":
    test_instance = LiLimParser.parse(
        "./pdp_100/pdp_100/lc101.txt")

    test_alns = ALNS(test_instance)
    empty_solution = Solution(test_instance)
    initial_solution = test_alns.iterate(empty_solution)

    print("Distance Matrix Shape:", test_instance.distance_matrix_.shape)
