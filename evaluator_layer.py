from problem_layer import ProblemInstance
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from solution_layer import Solution


class FeasibilityChecker:

    @staticmethod
    def is_valid_route(route: list[int], instance: ProblemInstance):
        assert route[0] == 0 and route[-1] == 0 and len(
            route) >= 2, "路线必须以0开头和结尾,且至少包含起点和终点"
        assert len(route) % 2 == 0, "每条路线上的任务数必须为偶数（成对的取货和送货）"
        return True

    @staticmethod
    def check_route(route: list[int], instance: ProblemInstance) -> bool:
        return FeasibilityChecker.check_capacity(route, instance) and FeasibilityChecker.check_time_windows(route,
                                                                                                            instance) and FeasibilityChecker.check_pickup_before_delivery(
            route, instance)

    @staticmethod
    def check_capacity(route: list[int], instance: ProblemInstance) -> bool:
        current_load = 0
        for task_id in route:
            task = instance.tasks_[task_id]
            current_load += task.demand_
            if current_load > instance.vehicle_capacity_:
                return False

        return True

    @staticmethod
    def check_time_windows(route: list[int], instance: ProblemInstance) -> bool:
        current_time = 0
        last_visit_task = 0
        for task_id in route:
            task = instance.tasks_[task_id]
            arrival_time = current_time + \
                instance.distance_matrix_[(last_visit_task, task_id)]
            if arrival_time < task.ready_time_:
                current_time = task.ready_time_ + task.service_time_
            elif arrival_time > task.due_time_:
                return False
            else:
                current_time = arrival_time + task.service_time_
            last_visit_task = task_id

        return True

    @staticmethod
    def check_pickup_before_delivery(route: list[int], instance: ProblemInstance) -> bool:
        vis = set()
        for task_id in route:
            task = instance.tasks_[task_id]
            if task.pickup_ > 0 and (task.pickup_ not in vis):
                return False
            vis.add(task_id)

        return True


class CostEvaluator:

    @staticmethod
    def route_cost(route: list[int], instance: ProblemInstance) -> float:
        last_task_id = 0
        cost = 0.0
        for task_id in route:
            cost += instance.distance_matrix_[(last_task_id, task_id)]
            last_task_id = task_id
        cost += instance.distance_matrix_[(last_task_id, 0)]
        return cost

    @staticmethod
    def solution_cost(solution: 'Solution', instance: ProblemInstance) -> float:
        total_cost = 0.0
        for route in solution.routes_:
            total_cost += CostEvaluator.route_cost(route, instance)
        return total_cost
