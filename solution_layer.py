from dataclasses import dataclass
from problem_layer import ProblemInstance
from evaluator_layer import CostEvaluator, FeasibilityChecker


@dataclass(slots=True)
class Solution:
    routes_: list[list[int]]  # 所有车辆路线
    assigned_requests_: set[int]  # 已分配的请求ID列表
    request_bank_: set[int]  # 未分配的请求ID列表
    solution_cost_: float = 0.0  # 总距离成本
    vehicle_count_: int = 0  # 使用的车辆数量

    @classmethod
    def from_instance(cls, instance: ProblemInstance) -> "Solution":
        return cls(routes_=[[0, 0] for _ in range(instance.number_of_vehicles_)], assigned_requests_=set(), request_bank_=set(instance.requests_.keys()))

    def update_cost_and_vehicle_count(self, instance: ProblemInstance) -> None:
        self.vehicle_count_ = sum(
            1 for route in self.routes_ if len(route) > 2)
        self.solution_cost_ = CostEvaluator.solution_cost(self, instance)

    def copy(self) -> "Solution":

        return Solution(
            routes_=[list(route) for route in self.routes_],
            assigned_requests_=set(self.assigned_requests_),
            request_bank_=set(self.request_bank_),
            solution_cost_=self.solution_cost_,
            vehicle_count_=self.vehicle_count_
        )

    def calculate_removal_cost_reduction(self, request_id: int, instance: ProblemInstance) -> float:
        pickup_id, delivery_id = instance.requests_[request_id]
        for route in self.routes_:
            if pickup_id in route and delivery_id in route:
                original_cost = CostEvaluator.route_cost(route, instance)

                new_route = [task_id for task_id in route if task_id not in (
                    pickup_id, delivery_id)]
                new_cost = CostEvaluator.route_cost(new_route, instance)

                return original_cost - new_cost

        return 0.0

    def best_insert(self, request_id: int,  route: list[int], instance: ProblemInstance) -> tuple[int, int, float]:
        # 一条路，插哪里最好
        pickup_id, delivery_id = instance.requests_[request_id]

        best_pickup_pos = -1
        best_delivery_pos = -1
        best_cost_increase = float('inf')

        assert route[0] == 0 and route[-1] == 0 and len(
            route) >= 2, "路线必须以0开头和结尾,且至少包含起点和终点"

        for pickup_pos in range(1, len(route)):
            for delivery_pos in range(pickup_pos, len(route)):
                new_route = route[:pickup_pos] + [pickup_id] + \
                    route[pickup_pos:delivery_pos] + \
                    [delivery_id] + route[delivery_pos:]
                if FeasibilityChecker.check_route(new_route, instance):
                    cost_increase = CostEvaluator.route_cost(
                        new_route, instance) - CostEvaluator.route_cost(route, instance)
                    if cost_increase < best_cost_increase:
                        best_cost_increase = cost_increase
                        best_pickup_pos = pickup_pos
                        best_delivery_pos = delivery_pos

        return best_pickup_pos, best_delivery_pos, best_cost_increase

    def greedy_insertion_cost_increase(self, request_id: int, instance: ProblemInstance) -> tuple[int, int, int, float]:
        # 所有路，插哪条路？哪里最好
        best_cost_increase = float('inf')
        best_pickup_pos = -1
        best_delivery_pos = -1
        best_insert_route_idx = -1
        for i, route in enumerate(self.routes_):
            pickup_pos, delivery_pos, cost_increase = self.best_insert(
                request_id, route, instance)
            if cost_increase < best_cost_increase:
                best_cost_increase = cost_increase
                best_pickup_pos = pickup_pos
                best_delivery_pos = delivery_pos
                best_insert_route_idx = i

        return best_insert_route_idx, best_pickup_pos, best_delivery_pos, best_cost_increase
