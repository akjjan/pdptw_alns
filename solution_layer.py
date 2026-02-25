from problem_layer import ProblemInstance
from evaluator_layer import CostEvaluator


class Solution:
    instance_: ProblemInstance
    routes_: list[list[int]]  # 所有车辆路线
    assigned_requests_: set[int]  # 已分配的请求ID列表
    request_bank_: set[int]  # 未分配的请求ID列表
    task_to_route_: dict[int, int]  # 任务->车辆
    solution_cost_: float = 0.0  # 总距离成本
    vehicle_count_: int = 0  # 使用的车辆数量

    def __str__(self):
        nonempty_routes = [route for route in self.routes_ if len(route) > 2]
        # 把每个非空路线隔行打印出来
        return f"路线: {nonempty_routes}\n" + \
            f"未分配的请求数量: {len(self.request_bank_)}\n" + \
            f"总距离成本: {self.solution_cost_}\n" + \
            f"使用的车辆数量: {self.vehicle_count_}"

    def __init__(self, instance: ProblemInstance):
        self.instance_ = instance
        self.routes_ = [[0, 0] for _ in range(instance.number_of_vehicles_)]
        self.assigned_requests_ = set()
        self.request_bank_ = set(instance.requests_.keys())
        self.task_to_route_ = {}

    def update_info(self) -> None:
        self.vehicle_count_ = sum(
            1 for route in self.routes_ if len(route) > 2)
        self.solution_cost_ = CostEvaluator.distance_cost(self, self.instance_)

    # 输入：请求， 路线， 位置 ；  输出：插入此请求的成本增加
    def calculate_insertion_cost_increase(self, request_id: int, route_idx: int, pickup_pos: int,
                                          delivery_pos: int) -> float:
        instance = self.instance_
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
    def calculate_removal_cost_reduction(self, request_id: int) -> float:
        instance = self.instance_

        pickup_id, delivery_id = instance.requests_[request_id]

        route = self.routes_[self.task_to_route_[pickup_id]]

        pickup_pos = route.index(pickup_id)
        delivery_pos = route.index(delivery_id)

        if pickup_pos + 1 == delivery_pos:
            after = route[delivery_pos + 1]
            before = route[pickup_pos - 1]

            ans = 0.0
            ans += instance.distance_matrix_[before, pickup_id]
            ans += instance.distance_matrix_[pickup_id, delivery_id]
            ans += instance.distance_matrix_[delivery_id, after]
            ans -= instance.distance_matrix_[before, after]
            return ans

        else:
            after_delivery = route[delivery_pos + 1]
            before_delivery = route[delivery_pos - 1]
            after_pickup = route[pickup_pos + 1]
            before_pickup = route[pickup_pos - 1]

            ans = 0.0
            ans += instance.distance_matrix_[before_pickup, pickup_id]
            ans += instance.distance_matrix_[pickup_id, after_pickup]
            ans += instance.distance_matrix_[before_delivery, delivery_id]
            ans += instance.distance_matrix_[delivery_id, after_delivery]

            ans -= instance.distance_matrix_[before_pickup, after_pickup]
            ans -= instance.distance_matrix_[before_delivery, after_delivery]

            return ans

    # 输入一个请求和一条路， 输出 ：插此路的哪里最好
    def best_insert(self, request_id: int, route_idx: int) -> tuple[int, int, float]:
        best_pickup_pos = -1
        best_delivery_pos = -1
        best_cost_increase = float('inf')

        route = self.routes_[route_idx]

        for pickup_pos in range(1, len(route)):
            for delivery_pos in range(pickup_pos, len(route)):

                cost_increase = self.calculate_insertion_cost_increase(
                    request_id, route_idx, pickup_pos, delivery_pos)

                if cost_increase < best_cost_increase:
                    # 这个函数只管插入，可行性这里不管
                    best_cost_increase = cost_increase
                    best_pickup_pos = pickup_pos
                    best_delivery_pos = delivery_pos

        return best_pickup_pos, best_delivery_pos, best_cost_increase
        # 返回： pickup插入位置， delivery插入位置， 最低的插入增加成本

    # 输入一个请求， 输出 ： 最好的插入位置
    def greedy_insert_cost_increase(self, request_id: int) -> tuple[int, int, int, float]:
        best_cost_increase = float('inf')
        best_pickup_pos = -1
        best_delivery_pos = -1
        best_insert_route_idx = -1

        for i, route in enumerate(self.routes_):
            pickup_pos, delivery_pos, cost_increase = self.best_insert(
                request_id, i)

            if cost_increase < best_cost_increase:
                best_cost_increase = cost_increase
                best_pickup_pos = pickup_pos
                best_delivery_pos = delivery_pos
                best_insert_route_idx = i

        return best_insert_route_idx, best_pickup_pos, best_delivery_pos, best_cost_increase
        # 返回： 路线， pickup插入位置，delivery插入位置， 最低的插入增加成本
