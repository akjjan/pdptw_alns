from solution_layer import Solution
from problem_layer import ProblemInstance, Task


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
        pass

    def iterate(self, solution: Solution) -> Solution:
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
        problem_instance = ProblemInstance(
            requests_={}, tasks_={}, distance_matrix_={}, delivery_to_pickup_={})
        with open(filepath, 'r') as f:
            k, q, s = map(int, f.readline().strip().split())
            # 读第一行
            problem_instance.number_of_vehicles_ = k
            problem_instance.vehicle_capacity_ = q

            _, depot_x, depot_y, *_ = map(int, f.readline().strip().split())
            # 读第二行仓库位置
            problem_instance.depot_x_ = depot_x
            problem_instance.depot_y_ = depot_y

            for line in f:
                task_id, x, y, demand, ready_time, due_time, service_time, pickup, delivery = map(
                    int, line.strip().split())
                problem_instance.tasks_[task_id] = Task(
                    id_=task_id,
                    x_=x,
                    y_=y,
                    demand_=demand,
                    ready_time_=ready_time,
                    due_time_=due_time,
                    service_time_=service_time,
                    _pickup=pickup,
                    delivery_=delivery
                )

            # 构建requests字典
        for task in problem_instance.tasks_.values():
            if task.delivery_ > 0:  # 取货任务
                problem_instance.requests_[task.id_] = task.delivery_

        problem_instance.delivery_to_pickup = {v: k for k, v in problem_instance.requests_.items()}

        for task1 in problem_instance.tasks_.values():
            for task2 in problem_instance.tasks_.values():
                dist = LiLimParser.calculate_distance(task1, task2)
                problem_instance.distance_matrix_[(
                    task1.id_, task2.id_)] = dist

        return problem_instance
