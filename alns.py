from solution_layer import Solution
from problem_layer import ProblemInstance, Task, Vehicle


class DestroyOperator:

    def destroy(self, solution: Solution, num_requests_to_remove: int) -> Solution:
        pass


class RepairOperator:

    def repair(self, solution: Solution) -> Solution:
        pass


class ALNS:

    def __init__(self, instance: ProblemInstance):
        self._instance = instance

    def iterate(self, solution: Solution) -> Solution:
        pass

    def select_destroy_operator(self):
        pass

    def select_repair_operator(self):
        pass


class LiLimParser:

    @staticmethod
    def calculate_distance(task1: Task, task2: Task) -> float:
        return ((task1._x - task2._x) ** 2 + (task1._y - task2._y) ** 2) ** 0.5

    @staticmethod
    def parse(filepath: str) -> ProblemInstance:
        problem_instance = ProblemInstance(
            _vehicles=[], _requests={}, _tasks={}, _distance_matrix={})
        with open(filepath, 'r') as f:
            K, Q, S = map(int, f.readline().strip().split())
            # 读第一行
            problem_instance._number_of_vehicles = K
            problem_instance._vehicle_capacity = Q

            _, depot_x, depot_y, *_ = map(int, f.readline().strip().split())
            # 读第二行仓库位置
            problem_instance._depot_x = depot_x
            problem_instance._depot_y = depot_y

            for line in f:
                task_id, x, y, demand, ready_time, due_time, service_time, pickup, delivery = map(
                    int, line.strip().split())
                problem_instance._tasks[task_id] = Task(
                    _id=task_id,
                    _x=x,
                    _y=y,
                    _demand=demand,
                    _ready_time=ready_time,
                    _due_time=due_time,
                    _service_time=service_time,
                    _pickup=pickup,
                    _delivery=delivery
                )

            # 构建requests字典
        for task in problem_instance._tasks.values():
            if task._delivery > 0:  # 取货任务
                problem_instance._requests[task._id] = task._delivery

        problem_instance._vehicles = [Vehicle(_vehicle_id=i) for i in range(K)]

        for task1 in problem_instance._tasks.values():
            for task2 in problem_instance._tasks.values():
                dist = LiLimParser.calculate_distance(task1, task2)
                problem_instance._distance_matrix[(
                    task1._id, task2._id)] = dist

        return problem_instance
