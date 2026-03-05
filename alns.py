from solution_layer import Solution
from problem_layer import ProblemInstance, Task
from evaluator_layer import FeasibilityChecker, CostEvaluator
from math import exp
import numpy as np
import copy
import random


class DestroyOperator:
    def __init__(self, num_requests_to_remove: int = 4, remove_greedy_index: float = 2.0):
        """
        Args:
            num_requests_to_remove (int): 一次破坏操作移除的请求数量
            remove_greedy_index (float): 控制移除随机性的参数，值越大，越接近贪心
        """
        self.num_requests_to_remove: int = num_requests_to_remove
        self.remove_greedy_index: float = remove_greedy_index

    @staticmethod
    def calculate_similarity(instance: ProblemInstance, req_id1: int, req_id2: int) -> float:
        """
        Args:
            instance (ProblemInstance): 问题实例
            req_id1 (int): 请求ID1
            req_id2 (int): 请求ID2
        Returns:
            similarity (float): 请求1和请求2的相似度,数值越小,表示越相似
        """
        pickup1, delivery1 = instance.requests[req_id1]
        pickup2, delivery2 = instance.requests[req_id2]

        pickup_task1 = instance.tasks[pickup1]
        delivery_task1 = instance.tasks[delivery1]
        pickup_task2 = instance.tasks[pickup2]
        delivery_task2 = instance.tasks[delivery2]

        similarity = 0.0

        similarity += instance.distance_mat[pickup1, pickup2]
        similarity += instance.distance_mat[delivery1, delivery2]
        similarity += abs(pickup_task1.ready_time - pickup_task2.ready_time)
        similarity += abs(delivery_task1.ready_time -
                          delivery_task2.ready_time)
        similarity += abs(pickup_task1.due_time - pickup_task2.due_time)
        similarity += abs(delivery_task1.due_time - delivery_task2.due_time)
        similarity += abs(pickup_task1.demand - pickup_task2.demand)

        return similarity

    def shaw_remove(self, solution: Solution) -> Solution:
        """
        移除一簇相似的请求
        Args:
            solution (Solution): 当前解
        Returns:
            new_solution (Solution): 经过Shaw移除操作后的新解
        """
        new_solution = copy.deepcopy(solution)
        r = random.choice(list(new_solution.assigned_requests))
        # 随机选择一个已分配的请求作为起点
        to_remove_reqs = set([r])
        # 待移除请求集合，初始包含起点请求

        sorted_to_remove_reqs = sorted(
            new_solution.assigned_requests,
            key=lambda req_id: DestroyOperator.calculate_similarity(new_solution.instance, r, req_id))
        # 按照与初始请求的相似度对已分配请求进行排序，越相似的请求越靠前

        y = self.remove_greedy_index

        to_remove_idx = [int((random.random() ** y) * len(sorted_to_remove_reqs))
                         for _ in range(self.num_requests_to_remove - 1)]
        # 选出与初始请求相似度较高的请求索引，数量为num_requests_to_remove-1

        for idx in to_remove_idx:
            to_remove_reqs.add(sorted_to_remove_reqs[idx])

        for req_id in to_remove_reqs:
            DestroyOperator.remove_inplace(new_solution, req_id)

        new_solution.update_info()

        return new_solution

    @staticmethod
    def remove_inplace(solution: Solution, request_id: int) -> None:
        """
        原地移除一个请求，避免在批量移除中反复拷贝。
        """
        instance = solution.instance
        pickup_id, delivery_id = instance.requests[request_id]

        route = solution.routes[solution.task_to_route[pickup_id]]
        route.remove(pickup_id)
        route.remove(delivery_id)

        solution.task_to_route[pickup_id] = -1
        solution.task_to_route[delivery_id] = -1
        solution.request_bank.add(request_id)
        solution.assigned_requests.remove(request_id)

    @staticmethod
    def remove(solution: Solution, request_id: int) -> Solution:
        """
        输入一个解和一个请求id，返回移除这个请求后的新解

        Args:
            solution (Solution): 当前解
            request_id (int): 要移除的请求ID
        Returns:
            solution: 移除请求后的新解
        """
        new_solution = copy.deepcopy(solution)
        # 把solution复制一份，修改复制的解
        DestroyOperator.remove_inplace(new_solution, request_id)
        new_solution.update_info()
        return new_solution
        # 输入一个解，返回移除request后的解

    def worst_random_remove(self, solution: Solution) -> Solution:
        """
        移除那些可能带来最大成本降低的请求,带有一定随机性
        Args:
            solution (Solution): 当前解
        Returns:
            new_solution (Solution): 经过worst random移除操作后的新解
        """
        num_requests_to_remove = self.num_requests_to_remove
        new_solution = copy.deepcopy(solution)
        sorted_assigned_requests = sorted(
            new_solution.assigned_requests,
            key=lambda req_id: new_solution.calculate_removal_cost_reduction(req_id), reverse=True)

        y = self.remove_greedy_index

        to_remove_idx = set(
            [int((random.random() ** y) * len(sorted_assigned_requests)) for _ in range(num_requests_to_remove)])

        for idx in to_remove_idx:
            DestroyOperator.remove_inplace(
                new_solution, sorted_assigned_requests[idx])

        new_solution.update_info()

        return new_solution
        # 输入一个解，移除num_requests_to_remove个请求，返回新的解

    def random_remove(self, solution: Solution) -> Solution:
        """
        随机移除一些请求
        Args:
            solution (Solution): 当前解
        Returns:
            new_solution (Solution): 经过随机移除操作后的新解
        """
        num_requests_to_remove = self.num_requests_to_remove
        to_remove_idx = random.sample(
            list(solution.assigned_requests), k=num_requests_to_remove)
        new_solution = copy.deepcopy(solution)
        for idx in to_remove_idx:
            DestroyOperator.remove_inplace(new_solution, idx)

        new_solution.update_info()
        return new_solution


class RepairOperator:
    def __init__(self, regret_k: int = 4):
        """
        Args:
            regret_k (int): 计算regret值时考虑的备选插入位置数量
        """
        self.regret_k: int = regret_k

    @staticmethod
    def swap_fix(solution: Solution) -> Solution:
        """
        交换修复操作, 对一个解中的每条路线的相邻任务进行交换。如果交换后可行且能改进成本，就保留交换结果，否则恢复原状。返回修复后的新解。
        Args:
            solution (Solution): 当前解
        Returns:
            new_solution (Solution): 经过交换修复操作后的新解
        """
        dist = solution.instance.distance_mat
        new_solution = copy.deepcopy(solution)
        routes = [r for r in new_solution.routes if len(r) > 2]
        for route in routes:
            for i in range(1, len(route) - 2):
                j = i + 1
                if dist[route[i-1], route[i]] + dist[route[i], route[j]] + dist[route[j], route[j+1]] > \
                        dist[route[i-1], route[j]] + dist[route[j], route[i]] + dist[route[i], route[j+1]]:
                    route[i], route[j] = route[j], route[i]
                    if FeasibilityChecker.check_route(route, new_solution.instance):
                        break
                    else:
                        route[i], route[j] = route[j], route[i]
        new_solution.update_info()
        return new_solution

    @staticmethod
    def insert_inplace(solution: Solution, request_id: int, route_idx: int, pickup_pos: int,
                       delivery_pos: int) -> None:
        """
        原地插入一个请求，避免在批量修复中反复拷贝。
        """
        instance = solution.instance
        pickup_id, delivery_id = instance.requests[request_id]

        route = solution.routes[route_idx]
        solution.routes[route_idx] = route[:pickup_pos] + [pickup_id] \
            + route[pickup_pos:delivery_pos] + \
            [delivery_id] + route[delivery_pos:]

        solution.task_to_route[pickup_id] = route_idx
        solution.task_to_route[delivery_id] = route_idx
        solution.assigned_requests.add(request_id)
        solution.request_bank.remove(request_id)

    @staticmethod
    def insert(solution: Solution, request_id: int, route_idx: int, pickup_pos: int,
               delivery_pos: int) -> Solution:
        new_solution = copy.deepcopy(solution)
        # 把solution复制一份，修改复制的
        RepairOperator.insert_inplace(new_solution, request_id,
                                      route_idx, pickup_pos, delivery_pos)

        new_solution.update_info()
        # 重新计算成本和车辆数
        return new_solution

    @staticmethod
    def greedy_repair(solution: Solution) -> Solution:
        """
        按照贪心插入成本增加把request bank里的请求插入到solution里，返回新的解
        """
        new_solution = copy.deepcopy(solution)
        # 把solution复制一份，修改复制的

        best_insert_route_idx: dict[int, int] = {}
        best_pickup_pos: dict[int, int] = {}
        best_delivery_pos: dict[int, int] = {}
        best_cost_increase: dict[int, float] = {}

        # 处理未分配的请求
        for request_id in new_solution.request_bank:
            best_insert_route_idx[request_id], best_pickup_pos[request_id], \
                best_delivery_pos[request_id], best_cost_increase[request_id] \
                = new_solution.greedy_insert_cost_increase(
                request_id)

        # 把未分配请求按照贪心插入成本增加排序
        sorted_unassigned_requests = sorted(
            new_solution.request_bank, key=lambda req_id: best_cost_increase[req_id])

        for request_id in sorted_unassigned_requests:
            if best_insert_route_idx[request_id] != -1:
                # 如果有可行的插入位置，就插入这个请求
                RepairOperator.insert_inplace(
                    new_solution, request_id, best_insert_route_idx[
                        request_id], best_pickup_pos[request_id],
                    best_delivery_pos[request_id])

        new_solution.update_info()

        return new_solution

        # 输入一个解，按照贪心插入成本增加把request bank里的请求插入到solution里，返回新的解

    def regret_repair(self, solution: Solution) -> Solution:
        """
        按照regret值把request bank里的请求插入到solution里，返回新的解
        """
        new_solution = copy.deepcopy(solution)
        to_insert_requests = sorted(list(
            new_solution.request_bank), key=lambda req: new_solution.regret_value(req, k=self.regret_k), reverse=True)
        for request_id in to_insert_requests:
            best_insert_route_idx, best_pickup_pos, best_delivery_pos, best_cost_increase = new_solution.greedy_insert_cost_increase(
                request_id)
            if best_insert_route_idx != -1:
                RepairOperator.insert_inplace(
                    new_solution, request_id, best_insert_route_idx, best_pickup_pos, best_delivery_pos)

        new_solution.update_info()
        return new_solution
        # 输入一个解，按照regret值把request bank里的请求插入到solution里，返回新的解


class ALNS:

    def __init__(self, instance: ProblemInstance):
        self.eps = 1e-6  # 用于比较浮点数的容差
        self.instance = instance  # 绑定问题实例
        self.vehicle_coef = 1e3  # 车辆数量系数
        self.distance_coef = 0.4 * self.vehicle_coef / instance.max_distance  # 距离系数
        self.time_coef = 0.4 * self.vehicle_coef / \
            instance.average_time_window_width  # 时间窗违约系数
        self.capacity_coef = 0.4 * self.vehicle_coef / instance.half_capacity  # 容量违约系数
        self.unassigned_coef = 1e3  # 未分配请求违约系数

        self.sigma1 = 8  # 全局最优改进奖励
        self.sigma2 = 4  # 当前解改进奖励
        self.sigma3 = 1  # 解被接受奖励

        self.rho = 0.2  # 权重更新的学习率
        self.alpha = 0.98  # 模拟退火的降温速率（加快降温）

        self.segment_length = 100
        self.segment_counter = 0

        self._stats = {
            "iterations": 0,
            "infeasible_rejected": 0,
            "better_accepted": 0,
            "worse_candidates": 0,
            "worse_accepted": 0,
        }
        self.best_feasible_solution = self.generate_initial_solution()  # 追踪最优可行解
        self.best_feasible_cost = self.calculate_obj(
            self.best_feasible_solution)  # 最优可行解的成本
        self.temperature = 0.01 * self.best_feasible_cost   # 模拟退火初始温度
        self.min_temperature = 0.001  # 模拟退火最低温度（改用固定绝对值，而非相对值）
        self.destroy_operators = DestroyOperator()
        self.repair_operators = RepairOperator()

        self.destroy_pool = [self.destroy_operators.shaw_remove,
                             self.destroy_operators.worst_random_remove, self.destroy_operators.random_remove]
        self.repair_pool = [self.repair_operators.greedy_repair,
                            self.repair_operators.regret_repair]

        self.destroy_weights = [1.0]*len(self.destroy_pool)
        self.repair_weights = [1.0]*len(self.repair_pool)

        self.destroy_scores = [0.0]*len(self.destroy_pool)
        self.repair_scores = [0.0]*len(self.repair_pool)

        self.destroy_uses = [0]*len(self.destroy_pool)
        self.repair_uses = [0]*len(self.repair_pool)

    def generate_initial_solution(self) -> Solution:
        """
        生成一个初始解
        """
        solution = Solution(self.instance)

        for request_id in list(solution.request_bank):
            pickup_id, delivery_id = self.instance.requests[request_id]

            to_insert_route_idx = min(
                range(len(solution.routes)), key=lambda idx: len(solution.routes[idx]))
            # 选择最短的路线插入请求

            route = solution.routes[to_insert_route_idx]
            # 定位到要插入的路线

            new_route = route[:-1] + [pickup_id, delivery_id, 0]
            # 直接连续插入到最后
            solution.task_to_route[pickup_id] = to_insert_route_idx
            solution.task_to_route[delivery_id] = to_insert_route_idx
            # 更新任务到路线的映射

            if FeasibilityChecker.check_route(new_route, self.instance):
                solution.routes[to_insert_route_idx] = new_route
                solution.request_bank.remove(request_id)
                solution.assigned_requests.add(request_id)
                # 如果插入后可行，更新路线、request bank和assigned requests

        solution.update_info()

        # 初始解可行则记录为最优可行解
        if FeasibilityChecker.check_solution(solution):
            self.best_feasible_solution = copy.deepcopy(solution)
            self.best_feasible_cost = self.calculate_obj(solution)

        return solution

    def calculate_obj(self, solution: Solution) -> float:
        """
        计算带罚项的目标函数值。
        车辆成本+距离成本+ 时间窗违约成本+容量违约成本+未分配请求违约成本
        """
        return self.vehicle_coef * solution.vehicle_count + \
            self.distance_coef * solution.distance_cost + \
            self.time_coef * CostEvaluator.calculate_time_window_violation(solution) + \
            self.capacity_coef * \
            CostEvaluator.calculate_capacity_violation(
                solution) + \
            self.unassigned_coef * len(solution.request_bank)

    def segment_update(self):
        """
        每个阶段更新算子权重
        """
        if self.segment_counter >= self.segment_length:
            for i in range(len(self.destroy_pool)):
                if self.destroy_uses[i] > 0:
                    self.destroy_weights[i] = (
                        1 - self.rho) * self.destroy_weights[i] + self.rho * self.destroy_scores[i] / self.destroy_uses[i]
                self.destroy_scores[i] = 0.0
                self.destroy_uses[i] = 0
            for i in range(len(self.repair_pool)):
                if self.repair_uses[i] > 0:
                    self.repair_weights[i] = (
                        1 - self.rho) * self.repair_weights[i] + self.rho * self.repair_scores[i] / self.repair_uses[i]
                self.repair_scores[i] = 0.0
                self.repair_uses[i] = 0
            self.segment_counter = 0

    def iterate(self, solution: Solution):
        destroy_idx, destroy_func = self.select_destroy_operator()
        repair_idx, repair_func = self.select_repair_operator()

        new_solution = destroy_func(solution)
        new_solution = repair_func(new_solution)

        self.destroy_uses[destroy_idx] += 1
        self.repair_uses[repair_idx] += 1
        self.segment_counter += 1
        self.temperature = max(
            self.temperature * self.alpha, self.min_temperature)  # 降温但不低于最低温度

        self._stats["iterations"] += 1

        result_solution = solution  # 默认返回原解

        if not FeasibilityChecker.check_pickup_before_delivery_for_solution(new_solution):
            self._stats["infeasible_rejected"] += 1
        else:
            new_solution = RepairOperator.swap_fix(new_solution)
            new_cost = self.calculate_obj(new_solution)
            old_cost = self.calculate_obj(solution)

            # 任何时候如果新解完全可行，就追踪最优可行解
            if FeasibilityChecker.check_solution(new_solution):
                if new_cost < self.best_feasible_cost - self.eps:
                    self.best_feasible_solution = copy.deepcopy(new_solution)
                    self.best_feasible_cost = new_cost
                    self.destroy_scores[destroy_idx] += self.sigma1
                    self.repair_scores[repair_idx] += self.sigma1

            if new_cost < old_cost - self.eps:
                # 如果新解明显改进
                self._stats["better_accepted"] += 1
                self.destroy_scores[destroy_idx] += self.sigma2 + self.sigma3
                self.repair_scores[repair_idx] += self.sigma2 + self.sigma3
                result_solution = new_solution
            elif new_cost > old_cost + self.eps:
                # 新解明显更差，用温度接受准则
                acceptance_bad_prob = exp(- (new_cost -
                                          old_cost) / self.temperature)
                self._stats["worse_candidates"] += 1
                if random.random() < acceptance_bad_prob:
                    self._stats["worse_accepted"] += 1
                    self.destroy_scores[destroy_idx] += self.sigma3
                    self.repair_scores[repair_idx] += self.sigma3
                    result_solution = new_solution
            else:
                # 差异在eps范围内，视为相等，直接接受
                result_solution = new_solution

        # 统一在末尾更新权重（每 segment_length 次触发）
        self.segment_update()
        return result_solution

    def select_destroy_operator(self):
        """
        根据权重随机选择一个破坏算子
        """
        probs = np.array(self.destroy_weights) / sum(self.destroy_weights)
        idx = np.random.choice(len(self.destroy_pool), p=probs)
        return idx, self.destroy_pool[idx]

    def select_repair_operator(self):
        """
        根据权重随机选择一个修复算子
        """
        probs = np.array(self.repair_weights) / sum(self.repair_weights)
        idx = np.random.choice(len(self.repair_pool), p=probs)
        return idx, self.repair_pool[idx]

    def get_stats(self) -> dict:
        return dict(self._stats)


class LiLimParser:

    @staticmethod
    def calculate_distance(task1: Task, task2: Task) -> float:
        return ((task1.x - task2.x) ** 2 + (task1.y - task2.y) ** 2) ** 0.5

    @staticmethod
    def parse(filepath: str) -> ProblemInstance:
        instance = ProblemInstance()
        with open(filepath, 'r') as f:
            k, q, s = map(int, f.readline().strip().split())
            # 读第一行
            instance.number_of_vehicles = k
            instance.vehicle_capacity = q

            instance.half_capacity = q / 2.0

            average_time_window_width = 0.0

            line_cnt = 0
            for line in f:
                task_id, x, y, demand, ready_time, due_time, service_time, pickup, delivery = map(
                    int, line.strip().split())
                if line_cnt > 0:
                    average_time_window_width += (due_time - ready_time)
                instance.tasks[task_id] = Task(
                    x=x,
                    y=y,
                    demand=demand,
                    ready_time=ready_time,
                    due_time=due_time,
                    service_time=service_time,
                    pickup=pickup,
                    delivery=delivery
                )
                line_cnt += 1

            instance.depot_x = instance.tasks[0].x
            instance.depot_y = instance.tasks[0].y
            instance.average_time_window_width = average_time_window_width / \
                (len(instance.tasks) - 1)

        # 构建requests字典
        request_id = 1
        for id_, task in instance.tasks.items():
            if task.delivery > 0:
                instance.requests[request_id] = (id_, task.delivery)
                instance.pickup_to_request[id_] = request_id
                instance.delivery_to_request[
                    task.delivery] = request_id
                request_id += 1

        instance.delivery_to_pickup = {
            v: k for k, v in instance.requests.values()}

        n = len(instance.tasks)
        instance.distance_mat = np.zeros((n, n))
        for i, task1 in instance.tasks.items():
            for j, task2 in instance.tasks.items():
                dist = LiLimParser.calculate_distance(task1, task2)
                instance.distance_mat[i, j] = dist
                instance.max_distance = max(instance.max_distance, dist)

        return instance
