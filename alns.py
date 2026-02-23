from solution_layer import Solution
from problem_layer import ProblemInstance, Task
from evaluator_layer import FeasibilityChecker


class DestroyOperator:

    @staticmethod
    def remove(solution: Solution, instance: ProblemInstance, request_id: int) -> Solution:
        pickup_id, delivery_id = instance.requests_[request_id]
        # 取货，送货任务
        new_solution = solution.copy()
        # 把solution复制一份，修改复制的
        for route in new_solution.routes_:
            if pickup_id in route and delivery_id in route:
                route.remove(pickup_id)
                route.remove(delivery_id)

        new_solution.request_bank_.add(request_id)
        new_solution.update_cost_and_vehicle_count(instance)
        return new_solution
        # 输入一个解，返回移除request后的解

    @staticmethod
    def worst_removal(solution: Solution, instance: ProblemInstance, num_requests_to_remove: int) -> Solution:
        new_solution = solution.copy()
        sorted_assigned_requests = sorted(
            new_solution.assigned_requests_, key=lambda req_id: new_solution.calculate_removal_cost_reduction(req_id, instance), reverse=True)

        for request_id in sorted_assigned_requests[:num_requests_to_remove]:
            new_solution = DestroyOperator.remove(
                new_solution, instance, request_id)

        return new_solution
        # 输入一个解，移除num_requests_to_remove个请求，返回新的解


class RepairOperator:

    def repair(self, solution: Solution) -> Solution:
        pass

    @staticmethod
    def insert(solution: Solution, instance: ProblemInstance, request_id: int, route_idx: int, pickup_pos: int, delivery_pos: int) -> Solution:
        pickup_id, delivery_id = instance.requests_[request_id]
        # 取货和送货任务id
        new_solution = solution.copy()
        # 把solution复制一份，修改复制的
        new_solution.routes_[route_idx].insert(pickup_pos, pickup_id)
        new_solution.routes_[route_idx].insert(delivery_pos + 1, delivery_id)
        # 插入pickup和delivery，注意delivery_pos要加1，因为插入pickup后delivery_pos会往后移一位
        new_solution.assigned_requests_.add(request_id)
        # 更新request bank和assigned requests
        new_solution.request_bank_.remove(request_id)
        new_solution.update_cost_and_vehicle_count(instance)
        # 重新计算成本和车辆数
        return new_solution

    @staticmethod
    def greedy_repair(solution: Solution, instance: ProblemInstance) -> Solution:
        new_solution = solution.copy()
        best_insert_route_idx: dict[int, int] = {}
        best_pickup_pos: dict[int, int] = {}
        best_delivery_pos: dict[int, int] = {}
        best_cost_increase: dict[int, float] = {}

        for request_id in new_solution.request_bank_:
            best_insert_route_idx[request_id], best_pickup_pos[request_id], best_delivery_pos[request_id], best_cost_increase[request_id] = new_solution.greedy_insertion_cost_increase(
                request_id, instance)

        # 把未分配请求按照贪心插入成本增加排序
        sorted_unassigned_requests = sorted(
            new_solution.request_bank_, key=lambda req_id: best_cost_increase[req_id])

        for request_id in sorted_unassigned_requests:
            if best_insert_route_idx[request_id] != -1:
                new_solution = RepairOperator.insert(
                    new_solution, instance, request_id, best_insert_route_idx[request_id], best_pickup_pos[request_id], best_delivery_pos[request_id])

        return new_solution

        # 输入一个解，按照贪心插入成本增加把request bank里的请求插入到solution里，返回新的解


class ALNS:

    def __init__(self, instance: ProblemInstance):
        self._instance = instance

    def generate_initial_solution(self) -> Solution:
        solution = Solution(routes_=[[0, 0] for _ in range(self._instance.number_of_vehicles_)],  assigned_requests_=set(), request_bank_=set(
            self._instance.requests_.keys()))

        for request_id in list(solution.request_bank_):
            pickup_id, delivery_id = self._instance.requests_[request_id]

            to_insert_route_idx = min(
                range(len(solution.routes_)), key=lambda idx: len(solution.routes_[idx]))

            route = solution.routes_[to_insert_route_idx]

            new_route = route[:-1] + [pickup_id, delivery_id, 0]

            if FeasibilityChecker.check_route(new_route, self._instance):
                solution.routes_[to_insert_route_idx] = new_route
                solution.request_bank_.remove(request_id)
                solution.assigned_requests_.add(request_id)

        solution.update_cost_and_vehicle_count(self._instance)

        return solution

    def iterate(self, solution: Solution):
        new_solution = DestroyOperator.worst_removal(
            solution, self._instance, num_requests_to_remove=3)
        new_solution = RepairOperator.greedy_repair(
            new_solution, self._instance)
        return new_solution

    def select_destroy_operator(self):
        pass

    def select_repair_operator(self):
        pass


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

            for line in f:
                task_id, x, y, demand, ready_time, due_time, service_time, pickup, delivery = map(
                    int, line.strip().split())
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

        # 构建requests字典
        request_id = 1
        for id, task in instance.tasks_.items():
            if task.delivery_ > 0:
                instance.requests_[request_id] = (id, task.delivery_)
                instance.pickup_to_request_[id] = request_id
                instance.delivery_to_request_[
                    task.delivery_] = request_id
                request_id += 1

        instance.delivery_to_pickup_ = {
            v: k for k, v in instance.requests_.values()}

        for i, task1 in instance.tasks_.items():
            for j, task2 in instance.tasks_.items():
                dist = LiLimParser.calculate_distance(task1, task2)
                instance.distance_matrix_[(
                    i, j)] = dist

        return instance
