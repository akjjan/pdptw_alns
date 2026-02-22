from alns import LiLimParser, ALNS

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
