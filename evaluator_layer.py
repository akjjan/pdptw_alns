from solution_layer import Route, Solution


class FeasibilityChecker:
    def check_route(self, route: Route) -> bool:
        pass

    def check_capacity(self, route: Route) -> bool:
        pass

    def check_time_windows(self, route: Route) -> bool:
        pass

    def check_pickup_before_delivery(self, route: Route) -> bool:
        pass


class CostEvaluator:
    def route_cost(self, route: Route) -> float:
        pass

    def solution_cost(self, solution: Solution) -> float:
        pass
