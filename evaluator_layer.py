from problem_layer import ProblemInstance
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from solution_layer import Solution


class FeasibilityChecker:

    '''检查一个解是否《真的》可行'''
    @staticmethod
    def check_solution(solution: 'Solution') -> bool:
        instance = solution.instance_
        for route in solution.routes_:
            if not FeasibilityChecker.check_route(route, instance):
                return False

        return True

    '''检查一条路线是否《真的》可行'''
    @staticmethod
    def check_route(route: list[int], instance: ProblemInstance) -> bool:
        return FeasibilityChecker.check_capacity(route, instance) and FeasibilityChecker.check_time_windows(route,
                                                                                                            instance) and FeasibilityChecker.check_pickup_before_delivery(
            route, instance)

    '''检查一条路线是否《真的》满足容量约束'''
    @staticmethod
    def check_capacity(route: list[int], instance: ProblemInstance) -> bool:
        current_load = 0
        for task_id in route:
            task = instance.tasks_[task_id]
            current_load += task.demand_
            if current_load > instance.vehicle_capacity_:
                return False

        return True

    '''计算一条路线的容量违约量'''
    @staticmethod
    def calculate_capacity_violation(route: list[int], instance: ProblemInstance) -> int:
        current_load: int = 0
        violation: int = 0
        for task_id in route:
            task = instance.tasks_[task_id]
            current_load += task.demand_
            if current_load > instance.vehicle_capacity_:
                violation = max(violation, current_load -
                                instance.vehicle_capacity_)
            if violation > 0.3 * instance.vehicle_capacity_:
                # 如果容量违约量太大，直接返回一个很大的数，表示这个解不可行
                return int(1e9)

        return violation

    '''检查一条路线是否《真的》满足时间窗约束'''
    @staticmethod
    def check_time_windows(route: list[int], instance: ProblemInstance) -> bool:
        current_time = 0
        last_visit_task = 0
        for task_id in route:
            task = instance.tasks_[task_id]
            arrival_time = current_time + \
                instance.distance_matrix_[last_visit_task, task_id]
            if arrival_time < task.ready_time_:
                current_time = task.ready_time_ + task.service_time_
            elif arrival_time > task.due_time_:
                return False
            else:
                current_time = arrival_time + task.service_time_
            last_visit_task = task_id

        return True

    '''计算一条路线的时间窗违约量'''
    @staticmethod
    def calculate_time_window_violation(route: list[int], instance: ProblemInstance) -> int:
        current_time = 0
        last_visit_task = 0
        violation = 0
        for task_id in route:
            task = instance.tasks_[task_id]
            arrival_time = current_time + \
                instance.distance_matrix_[last_visit_task, task_id]
            if arrival_time < task.ready_time_:
                current_time = task.ready_time_ + task.service_time_
            elif arrival_time > task.due_time_:
                violation = max(violation, arrival_time - task.due_time_)
                current_time = arrival_time + task.service_time_
            else:
                current_time = arrival_time + task.service_time_
            last_visit_task = task_id

            if violation > 0.2 * instance.average_time_window_width_:
                # 如果时间窗违约量太大，直接返回一个很大的数，表示这个解不可行
                return int(1e9)

        return violation

    '''检查一条路线是否《真的》满足先取后送约束'''
    @staticmethod
    def check_pickup_before_delivery(route: list[int], instance: ProblemInstance) -> bool:
        vis = set()
        for task_id in route:
            task = instance.tasks_[task_id]
            if task.pickup_ > 0 and (task.pickup_ not in vis):
                return False
            vis.add(task_id)

        return True

    '''检查一个解是否《真的》满足先取后送约束'''
    @staticmethod
    def check_pickup_before_delivery_for_solution(solution: 'Solution') -> bool:
        instance = solution.instance_
        for route in solution.routes_:
            if not FeasibilityChecker.check_pickup_before_delivery(route, instance):
                return False
        return True


class CostEvaluator:

    """算一条路线的距离"""
    @staticmethod
    def route_cost(route: list[int], instance: ProblemInstance) -> float:
        last_task_id = 0
        cost = 0.0
        for task_id in route:
            cost += instance.distance_matrix_[last_task_id, task_id]
            last_task_id = task_id
        cost += instance.distance_matrix_[last_task_id, 0]
        return cost

    '''算一个解的总距离'''
    @staticmethod
    def distance_cost(solution: 'Solution') -> float:
        instance = solution.instance_
        total_cost = 0.0
        for route in solution.routes_:
            total_cost += CostEvaluator.route_cost(route, instance)
        return total_cost

    @staticmethod
    def calculate_capacity_violation(solution: 'Solution') -> float:
        total_violation = 0.0
        instance = solution.instance_
        for route in solution.routes_:
            violation = FeasibilityChecker.calculate_capacity_violation(
                route, instance)
            if violation > 0.3 * instance.vehicle_capacity_:
                return 1e9
            total_violation += violation
        return total_violation

    @staticmethod
    def calculate_time_window_violation(solution: 'Solution') -> float:
        instance = solution.instance_
        total_violation = 0.0
        for route in solution.routes_:
            violation = FeasibilityChecker.calculate_time_window_violation(
                route, instance)
            if violation > 0.2 * instance.average_time_window_width_:
                return 1e9
            total_violation += violation
        return total_violation
