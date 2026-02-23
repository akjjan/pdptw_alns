from problem_layer import ProblemInstance
from evaluator_layer import CostEvaluator, FeasibilityChecker


class Solution:
    routes_: list[list[int]]  # 所有车辆路线
    assigned_requests_: set[int]  # 已分配的请求ID列表
    request_bank_: set[int]  # 未分配的请求ID列表
    task_to_route_: dict[int, int]  # 任务->车辆
    solution_cost_: float = 0.0  # 总距离成本
    vehicle_count_: int = 0  # 使用的车辆数量

    def __init__(self, instance: ProblemInstance):
        self.routes_ = [[0, 0] for _ in range(instance.number_of_vehicles_)]
        self.assigned_requests_ = set()
        self.request_bank_ = set(instance.requests_.keys())
        self.task_to_route_ = {}

    def update_cost_and_vehicle_count(self, instance: ProblemInstance) -> None:
        self.vehicle_count_ = sum(
            1 for route in self.routes_ if len(route) > 2)
        self.solution_cost_ = CostEvaluator.solution_cost(self, instance)

    # 计算在指定路线的指定位置插入的成本增加
    def calculate_insertion_cost_increase(self, request_id: int, route_idx: int, pickup_pos: int, delivery_pos: int, instance: ProblemInstance) -> float:
        pickup_id, delivery_id = instance.requests_[request_id]
        route = self.routes_[route_idx]

        if pickup_pos == delivery_pos:
            after = route[delivery_pos]
            before = route[delivery_pos - 1]
            ans = 0.0
            ans += instance.distance_matrix_[before, pickup_id]
            ans += instance.distance_matrix_[pickup_id, delivery_id]
            ans += instance.distance_matrix_[delivery_id, after]
            ans -= instance.distance_matrix_[before, after]
            return ans

        else:
            after_delivery = route[delivery_pos]
            before_delivery = route[delivery_pos - 1]
            after_pickup = route[pickup_pos]
            before_pickup = route[pickup_pos - 1]

            ans = 0.0
            ans += instance.distance_matrix_[before_pickup, pickup_id]
            ans += instance.distance_matrix_[pickup_id, after_pickup]
            ans += instance.distance_matrix_[before_delivery, delivery_id]
            ans += instance.distance_matrix_[delivery_id, after_delivery]

            ans -= instance.distance_matrix_[before_pickup, after_pickup]
            ans -= instance.distance_matrix_[before_delivery, after_delivery]

            return ans

    # 计算移除一个request的成本减少，前提是这个request已经被分配了
    def calculate_removal_cost_reduction(self, request_id: int, instance: ProblemInstance) -> float:
        pickup_id, delivery_id = instance.requests_[request_id]

        route = self.routes_[self.task_to_route_[pickup_id]]

        pickup_pos = route.index(pickup_id)
        delivery_pos = route.index(delivery_id)

        if pickup_pos + 1 == delivery_pos:
            after = route[delivery_pos+1]
            before = route[pickup_pos-1]

            ans = 0.0
            ans += instance.distance_matrix_[before, pickup_id]
            ans += instance.distance_matrix_[pickup_id, delivery_id]
            ans += instance.distance_matrix_[delivery_id, after]
            ans -= instance.distance_matrix_[before, after]
            return ans

        else:
            after_delivery = route[delivery_pos+1]
            before_delivery = route[delivery_pos-1]
            after_pickup = route[pickup_pos+1]
            before_pickup = route[pickup_pos-1]

            ans = 0.0
            ans += instance.distance_matrix_[before_pickup, pickup_id]
            ans += instance.distance_matrix_[pickup_id, after_pickup]
            ans += instance.distance_matrix_[before_delivery, delivery_id]
            ans += instance.distance_matrix_[delivery_id, after_delivery]

            ans -= instance.distance_matrix_[before_pickup, after_pickup]
            ans -= instance.distance_matrix_[before_delivery, after_delivery]

            return ans

    def best_insert(self, request_id: int,  route_idx: int, instance: ProblemInstance) -> tuple[int, int, float]:
        # 一条路，插哪里最好
        pickup_id, delivery_id = instance.requests_[request_id]

        best_pickup_pos = -1
        best_delivery_pos = -1
        best_cost_increase = float('inf')

        route = self.routes_[route_idx]
        for pickup_pos in range(1, len(route)):
            for delivery_pos in range(pickup_pos, len(route)):
                cost_increase = self.calculate_insertion_cost_increase(
                    request_id, route_idx, pickup_pos, delivery_pos, instance)
                if cost_increase < best_cost_increase:
                    # 只管插入，可行性这里不管
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
                request_id, i, instance)
            if cost_increase < best_cost_increase:
                best_cost_increase = cost_increase
                best_pickup_pos = pickup_pos
                best_delivery_pos = delivery_pos
                best_insert_route_idx = i

        return best_insert_route_idx, best_pickup_pos, best_delivery_pos, best_cost_increase
