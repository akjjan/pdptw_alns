from solution_layer import Solution
from problem_layer import ProblemInstance, Task
from evaluator_layer import FeasibilityChecker, CostEvaluator


class DestroyOperator:

    def destroy(self, solution: Solution, num_requests_to_remove: int) -> Solution:
        pass


class RepairOperator:

    def repair(self, solution: Solution) -> Solution:
        pass


class ALNS:

    def __init__(self, instance: ProblemInstance):
        self._instance = instance

    def generate_initial_solution(self) -> Solution:
        solution = Solution(routes_=[[0, 0] for _ in range(self._instance.number_of_vehicles_)], request_bank_=list(
            self._instance.requests_.keys()))

        for request_id in solution.request_bank_[:]:
            pickup_id, delivery_id = self._instance.requests_[request_id]

            to_insert_route_idx = min(
                range(len(solution.routes_)), key=lambda idx: len(solution.routes_[idx]))

            route = solution.routes_[to_insert_route_idx]

            new_route = route[:-1] + [pickup_id, delivery_id, 0]

            if FeasibilityChecker.check_route(new_route, self._instance):
                solution.routes_[to_insert_route_idx] = new_route
                solution.request_bank_.remove(request_id)

        solution.solution_cost_ = CostEvaluator.solution_cost(
            solution, self._instance)
        solution.vehicle_count_ = sum(
            1 for route in solution.routes_ if len(route) > 2)

        return solution

    def iterate(self, solution: Solution):
        pass

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
