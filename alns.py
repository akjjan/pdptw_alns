from solution_layer import Solution
from problem_layer import ProblemInstance, Task
from evaluator_layer import FeasibilityChecker, CostEvaluator
import numpy as np
import copy
import random


class DestroyOperator:
    num_requests_to_remove_: int = 3  # 一次破坏操作移除的请求数量
    y_: float = 3.0  # 控制随机移除的参数，y越大就越接近贪心

    @staticmethod
    def remove(solution: Solution, request_id: int) -> Solution:
        instance = solution.instance_
        pickup_id, delivery_id = instance.requests_[request_id]
        # 取货，送货任务
        new_solution = copy.deepcopy(solution)
        # 把solution复制一份，修改复制的解
        route = new_solution.routes_[new_solution.task_to_route_[pickup_id]]
        # 获得引用，直接修改这个route就行了
        route.remove(pickup_id)
        route.remove(delivery_id)

        new_solution.task_to_route_[pickup_id] = -1
        new_solution.task_to_route_[delivery_id] = -1
        # 更新任务到路线的映射

        new_solution.request_bank_.add(request_id)
        new_solution.assigned_requests_.remove(request_id)
        # 更新request bank和assigned requests
        new_solution.update_info()
        return new_solution
        # 输入一个解，返回移除request后的解

    def random_worst_remove(self, solution: Solution) -> Solution:
        num_requests_to_remove = self.num_requests_to_remove_
        new_solution = copy.deepcopy(solution)
        sorted_assigned_requests = sorted(
            new_solution.assigned_requests_,
            key=lambda req_id: new_solution.calculate_removal_cost_reduction(req_id), reverse=True)

        y = self.y_

        to_remove_idx = set(
            [int((random.random() ** y) * len(sorted_assigned_requests)) for _ in range(num_requests_to_remove)])

        for idx in to_remove_idx:
            new_solution = DestroyOperator.remove(
                new_solution, sorted_assigned_requests[idx])

        return new_solution
        # 输入一个解，移除num_requests_to_remove个请求，返回新的解

    def random_remove(self, solution: Solution) -> Solution:
        num_requests_to_remove = self.num_requests_to_remove_
        to_remove_idx = random.sample(
            list(solution.assigned_requests_), k=num_requests_to_remove)
        new_solution = copy.deepcopy(solution)
        for idx in to_remove_idx:
            new_solution = DestroyOperator.remove(new_solution, idx)
        return new_solution


class RepairOperator:
    regret_k: int = 3

    def repair(self, solution: Solution) -> Solution:
        pass

    @staticmethod
    def insert(solution: Solution, request_id: int, route_idx: int, pickup_pos: int,
               delivery_pos: int) -> Solution:
        instance = solution.instance_
        pickup_id, delivery_id = instance.requests_[request_id]
        # 取货和送货任务id
        new_solution = copy.deepcopy(solution)
        # 把solution复制一份，修改复制的
        new_solution.routes_[route_idx] = solution.routes_[route_idx][:pickup_pos] + [pickup_id] \
            + solution.routes_[route_idx][pickup_pos:delivery_pos] + \
            [delivery_id] + solution.routes_[route_idx][delivery_pos:]
        # 在指定路线的指定位置插入取货和送货任务

        new_solution.task_to_route_[pickup_id] = route_idx
        new_solution.task_to_route_[delivery_id] = route_idx
        # 更新任务到路线的映射

        new_solution.assigned_requests_.add(request_id)
        # 更新request bank和assigned requests
        new_solution.request_bank_.remove(request_id)

        new_solution.update_info()
        # 重新计算成本和车辆数
        return new_solution

    @staticmethod
    def greedy_repair(solution: Solution) -> Solution:

        new_solution = copy.deepcopy(solution)
        # 把solution复制一份，修改复制的

        best_insert_route_idx: dict[int, int] = {}
        best_pickup_pos: dict[int, int] = {}
        best_delivery_pos: dict[int, int] = {}
        best_cost_increase: dict[int, float] = {}

        # 处理未分配的请求
        for request_id in new_solution.request_bank_:
            best_insert_route_idx[request_id], best_pickup_pos[request_id], \
                best_delivery_pos[request_id], best_cost_increase[request_id] \
                = new_solution.greedy_insert_cost_increase(
                request_id)

        # 把未分配请求按照贪心插入成本增加排序
        sorted_unassigned_requests = sorted(
            new_solution.request_bank_, key=lambda req_id: best_cost_increase[req_id])

        for request_id in sorted_unassigned_requests:
            if best_insert_route_idx[request_id] != -1:
                # 如果有可行的插入位置，就插入这个请求
                new_solution = RepairOperator.insert(
                    new_solution, request_id, best_insert_route_idx[
                        request_id], best_pickup_pos[request_id],
                    best_delivery_pos[request_id])

        return new_solution

        # 输入一个解，按照贪心插入成本增加把request bank里的请求插入到solution里，返回新的解

    @staticmethod
    def regret_repair(solution: Solution) -> Solution:
        new_solution = copy.deepcopy(solution)
        to_insert_requests = sorted(list(
            new_solution.request_bank_), key=lambda req: new_solution.regret_value(req, k=3), reverse=True)
        for request_id in to_insert_requests:
            best_insert_route_idx, best_pickup_pos, best_delivery_pos, best_cost_increase = new_solution.greedy_insert_cost_increase(
                request_id)
            if best_insert_route_idx != -1:
                new_solution = RepairOperator.insert(
                    new_solution, request_id, best_insert_route_idx, best_pickup_pos, best_delivery_pos)

        return new_solution
        # 输入一个解，按照regret值把request bank里的请求插入到solution里，返回新的解


class ALNS:

    def __init__(self, instance: ProblemInstance):
        self.instance_ = instance
        self.a1_ = 1e3  # 车辆数量系数
        self.a2_ = self.a1_ / instance.max_distance_  # 距离系数
        self.a3_ = self.a1_ / instance.average_time_window_width_  # 时间窗违约系数
        self.a4_ = self.a1_ / instance.half_capacity_  # 容量违约系数
        self.a5_ = 1e3  # 未分配请求系数
        self._stats = {
            "iterations": 0,
            "infeasible_rejected": 0,
            "better_accepted": 0,
            "worse_candidates": 0,
            "worse_accepted": 0,
        }
        self.best_feasible_solution_ = Solution(instance)
        self.best_feasible_cost = float('inf')
        self.destroy_operators_ = DestroyOperator()
        self.repair_operators_ = RepairOperator()

    # 生成一个可行的初始解
    def generate_initial_solution(self) -> Solution:
        solution = Solution(self.instance_)

        for request_id in list(solution.request_bank_):
            pickup_id, delivery_id = self.instance_.requests_[request_id]

            to_insert_route_idx = min(
                range(len(solution.routes_)), key=lambda idx: len(solution.routes_[idx]))
            # 选择最短的路线插入请求

            route = solution.routes_[to_insert_route_idx]
            # 定位到要插入的路线

            new_route = route[:-1] + [pickup_id, delivery_id, 0]
            # 直接连续插入到最后
            solution.task_to_route_[pickup_id] = to_insert_route_idx
            solution.task_to_route_[delivery_id] = to_insert_route_idx
            # 更新任务到路线的映射

            if FeasibilityChecker.check_route(new_route, self.instance_):
                solution.routes_[to_insert_route_idx] = new_route
                solution.request_bank_.discard(request_id)
                solution.assigned_requests_.add(request_id)
                # 如果插入后可行，更新路线、request bank和assigned requests

        solution.update_info()

        # 初始解可行则记录为最优可行解
        if FeasibilityChecker.check_solution(solution):
            self.best_feasible_solution_ = copy.deepcopy(solution)
            self.best_feasible_cost = self.calculate_all_cost(solution)

        return solution

    # 车辆成本+距离成本+ 时间窗违约成本+容量违约成本
    def calculate_all_cost(self, solution: Solution) -> float:
        return self.a1_ * solution.vehicle_count_ + \
            self.a2_ * solution.solution_cost_ + \
            self.a3_ * CostEvaluator.calculate_time_window_violation(solution) + \
            self.a4_ * \
            CostEvaluator.calculate_capacity_violation(
                solution) + \
            self.a5_ * len(solution.request_bank_)

    def iterate(self, solution: Solution):
        destroy_operator = self.destroy_operators_
        repair_operator = self.repair_operators_

        a, b = random.random(), random.random()
        if a < 0.5:
            new_solution = destroy_operator.random_worst_remove(solution)
        else:
            new_solution = destroy_operator.random_remove(solution)
        if b < 0.5:
            new_solution = repair_operator.greedy_repair(new_solution)
        else:
            new_solution = repair_operator.regret_repair(new_solution)

        acceptance_bad_prob = 0.05
        self._stats["iterations"] += 1

        if not FeasibilityChecker.check_pickup_before_delivery_for_solution(new_solution):
            self._stats["infeasible_rejected"] += 1
            return solution
        else:
            new_cost = self.calculate_all_cost(new_solution)
            old_cost = self.calculate_all_cost(solution)

            # 任何时候如果新解完全可行，就追踪最优可行解
            if FeasibilityChecker.check_solution(new_solution):
                if self.best_feasible_solution_ is None or new_cost < self.best_feasible_cost:
                    self.best_feasible_solution_ = copy.deepcopy(new_solution)
                    self.best_feasible_cost = new_cost

            if new_cost < old_cost:
                self._stats["better_accepted"] += 1
                return new_solution
            else:
                self._stats["worse_candidates"] += 1
                if random.random() < acceptance_bad_prob:
                    self._stats["worse_accepted"] += 1
                    return new_solution
                else:
                    return solution

    def select_destroy_operator(self):
        pass

    def select_repair_operator(self):
        pass

    def get_stats(self) -> dict:
        return dict(self._stats)


class LiLimParser:

    @staticmethod
    def calculate_distance(task1: Task, task2: Task) -> float:
        return ((task1.x_ - task2.x_) ** 2 + (task1.y_ - task2.y_) ** 2) ** 0.5

    @staticmethod
    def parse(filepath: str) -> ProblemInstance:
        instance = ProblemInstance()
        with open(filepath, 'r') as f:
            k, q, s = map(int, f.readline().strip().split())
            # 读第一行
            instance.number_of_vehicles_ = k
            instance.vehicle_capacity_ = q

            instance.half_capacity_ = q / 2.0

            average_time_window_width = 0.0
            for line in f:
                task_id, x, y, demand, ready_time, due_time, service_time, pickup, delivery = map(
                    int, line.strip().split())
                average_time_window_width += (due_time - ready_time)
                instance.tasks_[task_id] = Task(
                    x_=x,
                    y_=y,
                    demand_=demand,
                    ready_time_=ready_time,
                    due_time_=due_time,
                    service_time_=service_time,
                    pickup_=pickup,
                    delivery_=delivery
                )

            instance.depot_x_ = instance.tasks_[0].x_
            instance.depot_y_ = instance.tasks_[0].y_
            instance.average_time_window_width_ = average_time_window_width / \
                len(instance.tasks_)

        # 构建requests字典
        request_id = 1
        for id_, task in instance.tasks_.items():
            if task.delivery_ > 0:
                instance.requests_[request_id] = (id_, task.delivery_)
                instance.pickup_to_request_[id_] = request_id
                instance.delivery_to_request_[
                    task.delivery_] = request_id
                request_id += 1

        instance.delivery_to_pickup_ = {
            v: k for k, v in instance.requests_.values()}

        n = len(instance.tasks_)
        instance.distance_matrix_ = np.zeros((n, n))
        for i, task1 in instance.tasks_.items():
            for j, task2 in instance.tasks_.items():
                dist = LiLimParser.calculate_distance(task1, task2)
                instance.distance_matrix_[i, j] = dist
                instance.max_distance_ = max(instance.max_distance_, dist)

        return instance
