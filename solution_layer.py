from problem_layer import ProblemInstance
from evaluator_layer import CostEvaluator, FeasibilityChecker
import random


class Solution:
    instance: ProblemInstance
    routes: list[list[int]]  # 所有车辆路线
    assigned_requests: set[int]  # 已分配的请求ID列表
    request_bank: set[int]  # 未分配的请求ID列表
    task_to_route: dict[int, int]  # 任务->车辆
    distance_cost: float = 0.0  # 总距离成本
    vehicle_count: int = 0  # 使用的车辆数量

    arrival: dict[int, int]  # 键：任务ID，值：到达时间
    load: dict[int, int]  # 键：任务ID，值：当前负载

    def __str__(self):
        """
        返回解的字符串表示，包括每条路线的任务列表、未分配请求数量、总距离成本和使用的车辆数量。
        """
        nonempty_routes = [route for route in self.routes if len(route) > 2]
        # 把每个非空路线隔行打印出来
        return f"路线: {nonempty_routes}\n" + \
            f"未分配的请求数量: {len(self.request_bank)}\n" + \
            f"总距离成本: {self.distance_cost:.2f}\n" + \
            f"使用的车辆数量: {self.vehicle_count}"

    def __init__(self, instance: ProblemInstance):
        self.instance = instance
        self.routes = [[0, 0] for _ in range(instance.number_of_vehicles)]
        self.assigned_requests = set()
        self.request_bank = set(instance.requests.keys())
        self.task_to_route = {}
        self.arrival = {}
        self.load = {}

    def __deepcopy__(self, memo):
        """
        定制深拷贝: 问题实例在搜索期间视为只读，直接共享引用；
        仅复制会被算子修改的可变结构。
        """
        obj_id = id(self)
        if obj_id in memo:
            return memo[obj_id]

        cls = self.__class__
        new_solution = cls.__new__(cls)
        memo[obj_id] = new_solution

        new_solution.instance = self.instance
        new_solution.routes = [route[:] for route in self.routes]
        new_solution.assigned_requests = self.assigned_requests.copy()
        new_solution.request_bank = self.request_bank.copy()
        new_solution.task_to_route = self.task_to_route.copy()
        new_solution.distance_cost = self.distance_cost
        new_solution.vehicle_count = self.vehicle_count
        new_solution.arrival = self.arrival.copy()
        new_solution.load = self.load.copy()

        return new_solution

    def update_info(self) -> None:
        """
        更新解的距离成本、使用的车辆数量。
        """
        self.vehicle_count = sum(
            1 for route in self.routes if len(route) > 2)
        self.distance_cost = CostEvaluator.distance_cost(self)

    def calculate_insertion_cost_increase(self, request_id: int, route_idx: int, pickup_pos: int,
                                          delivery_pos: int) -> float:
        """
        计算将一个请求插入到指定路线和位置的成本增加。有随机噪声，增强随机性。
        """
        instance = self.instance
        pickup_id, delivery_id = instance.requests[request_id]
        route = self.routes[route_idx]

        maxn = 0.01 * self.instance.max_distance
        noise = random.uniform(-maxn, maxn)

        if pickup_pos == delivery_pos:
            after = route[delivery_pos]
            before = route[delivery_pos - 1]
            ans = 0.0
            ans += instance.distance_mat[before, pickup_id]
            ans += instance.distance_mat[pickup_id, delivery_id]
            ans += instance.distance_mat[delivery_id, after]
            ans -= instance.distance_mat[before, after]
            return max(0.0, ans + noise)

        else:
            after_delivery = route[delivery_pos]
            before_delivery = route[delivery_pos - 1]
            after_pickup = route[pickup_pos]
            before_pickup = route[pickup_pos - 1]

            ans = 0.0
            ans += instance.distance_mat[before_pickup, pickup_id]
            ans += instance.distance_mat[pickup_id, after_pickup]
            ans += instance.distance_mat[before_delivery, delivery_id]
            ans += instance.distance_mat[delivery_id, after_delivery]

            ans -= instance.distance_mat[before_pickup, after_pickup]
            ans -= instance.distance_mat[before_delivery, after_delivery]

            return max(0.0, ans + noise)

    def calculate_removal_cost_reduction(self, request_id: int) -> float:
        """
        计算移除一个已分配请求的成本减少。有随机噪声，增强随机性。
        """
        instance = self.instance

        pickup_id, delivery_id = instance.requests[request_id]

        route = self.routes[self.task_to_route[pickup_id]]

        pickup_pos = route.index(pickup_id)
        delivery_pos = route.index(delivery_id)

        maxn = 0.01 * self.instance.max_distance
        noise = random.uniform(-maxn, maxn)

        if pickup_pos + 1 == delivery_pos:
            after = route[delivery_pos + 1]
            before = route[pickup_pos - 1]

            ans = 0.0
            ans += instance.distance_mat[before, pickup_id]
            ans += instance.distance_mat[pickup_id, delivery_id]
            ans += instance.distance_mat[delivery_id, after]
            ans -= instance.distance_mat[before, after]
            return max(0.0, ans + noise)

        else:
            after_delivery = route[delivery_pos + 1]
            before_delivery = route[delivery_pos - 1]
            after_pickup = route[pickup_pos + 1]
            before_pickup = route[pickup_pos - 1]

            ans = 0.0
            ans += instance.distance_mat[before_pickup, pickup_id]
            ans += instance.distance_mat[pickup_id, after_pickup]
            ans += instance.distance_mat[before_delivery, delivery_id]
            ans += instance.distance_mat[delivery_id, after_delivery]

            ans -= instance.distance_mat[before_pickup, after_pickup]
            ans -= instance.distance_mat[before_delivery, after_delivery]

            return max(0.0, ans + noise)

    def best_insert(self, request_id: int, route_idx: int) -> tuple[int, int, float]:
        """
        Args:
            request_id: 要插入的请求ID
            route_idx: 要插入的路线索引
        Returns:
            pickup_pos: 最佳pickup插入位置
            delivery_pos: 最佳delivery插入位置
            best_cost_increase: 最佳插入位置的成本增加
        """
        pickup_id, delivery_id = self.instance.requests[request_id]

        best_pickup_pos = -1
        best_delivery_pos = -1
        best_cost_increase = float('inf')
        tie_epsilon = 1e-6

        route = self.routes[route_idx]

        for pickup_pos in range(1, len(route)):
            for delivery_pos in range(pickup_pos, len(route)):

                cost_increase = self.calculate_insertion_cost_increase(
                    request_id, route_idx, pickup_pos, delivery_pos)

                new_route = route[:pickup_pos] + [pickup_id] + \
                    route[pickup_pos:delivery_pos] + [delivery_id] + \
                    route[delivery_pos:]

                if not FeasibilityChecker.check_route(new_route, self.instance):
                    # 如果这个插入位置不可行，直接跳过，不考虑它的成本增加
                    continue

                if cost_increase < best_cost_increase - tie_epsilon:
                    best_cost_increase = cost_increase
                    best_pickup_pos = pickup_pos
                    best_delivery_pos = delivery_pos
                elif abs(cost_increase - best_cost_increase) <= tie_epsilon:
                    if random.random() < 0.5:
                        best_cost_increase = cost_increase
                        best_pickup_pos = pickup_pos
                        best_delivery_pos = delivery_pos

        return best_pickup_pos, best_delivery_pos, best_cost_increase

    def greedy_insert_cost_increase(self, request_id: int) -> tuple[int, int, int, float]:
        """
        给定一个请求ID,计算将其插入到每条路线的最佳位置的成本增加,并返回成本增加最小的插入位置。
        """
        best_cost_increase = float('inf')
        best_pickup_pos = -1
        best_delivery_pos = -1
        best_insert_route_idx = -1

        for i, route in enumerate(self.routes):
            pickup_pos, delivery_pos, cost_increase = self.best_insert(
                request_id, i)

            if cost_increase < best_cost_increase:
                best_cost_increase = cost_increase
                best_pickup_pos = pickup_pos
                best_delivery_pos = delivery_pos
                best_insert_route_idx = i

        return best_insert_route_idx, best_pickup_pos, best_delivery_pos, best_cost_increase
        # 返回： 路线， pickup插入位置，delivery插入位置， 最低的插入增加成本

    def regret_value(self, request_id: int, k: int) -> float:
        """
        计算给定请求的后悔值。插入此请求的第k好位置的成本增加 - 最好位置的成本增加
        """
        cost_increases = []
        for i in range(len(self.routes)):
            _, _, cost_increase = self.best_insert(request_id, i)
            cost_increases.append(cost_increase)

        cost_increases.sort()
        if len(cost_increases) < k:
            raise ValueError(
                f"路线不足{k}个，无法计算后悔值")
        else:
            return cost_increases[k - 1] - cost_increases[0]
