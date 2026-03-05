from problem_layer import ProblemInstance
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from solution_layer import Solution


class FeasibilityChecker:

    @staticmethod
    def check_solution(solution: 'Solution') -> bool:
        """
        检查一个解是否满足所有约束
        """
        instance = solution.instance
        for route in solution.routes:
            if not FeasibilityChecker.check_route(route, instance):
                return False

        return True

    @staticmethod
    def check_route(route: list[int], instance: ProblemInstance) -> bool:
        """
        检查一条路线是否满足所有约束
        """
        return FeasibilityChecker.check_capacity(route, instance) and FeasibilityChecker.check_time_windows(route,
                                                                                                            instance) and FeasibilityChecker.check_pickup_before_delivery(
            route, instance)

    @staticmethod
    def check_capacity(route: list[int], instance: ProblemInstance) -> bool:
        """
        检查一条路线是否满足容量约束
        """
        current_load = 0
        capacity = 1.3 * instance.vehicle_capacity  # 允许一定程度的容量违约
        for task_id in route:
            task = instance.tasks[task_id]
            current_load += task.demand
            if current_load > capacity:
                return False

        return True

    @staticmethod
    def calculate_capacity_violation(route: list[int], instance: ProblemInstance) -> int:
        """
        计算一条路线的最大容量违约量
        """
        current_load: int = 0
        violation: int = 0
        for task_id in route:
            task = instance.tasks[task_id]
            current_load += task.demand
            if current_load > instance.vehicle_capacity:
                violation = max(violation, current_load -
                                instance.vehicle_capacity)
            if violation > 0.3 * instance.vehicle_capacity:
                # 如果容量违约量太大，直接返回一个很大的数
                return int(1e9)

        return violation

    @staticmethod
    def check_time_windows(route: list[int], instance: ProblemInstance) -> bool:
        """
        检查一条路线是否满足时间窗约束
        """
        current_time: int = 0
        last_visit_task: int = 0
        for task_id in route:
            task = instance.tasks[task_id]
            due_time = task.due_time + 0.3 * instance.average_time_window_width
            arrival_time = current_time + \
                instance.distance_mat[last_visit_task, task_id]
            if arrival_time < task.ready_time:
                current_time = task.ready_time + task.service_time
            elif arrival_time > due_time:
                return False
            else:
                current_time = arrival_time + task.service_time
            last_visit_task = task_id

        return True

    @staticmethod
    def calculate_time_window_violation(route: list[int], instance: ProblemInstance) -> int:
        """
        计算一条路线的时间窗违约量
        """
        current_time: int = 0
        last_visit_task: int = 0
        violation: int = 0
        for task_id in route:
            task = instance.tasks[task_id]
            arrival_time = current_time + \
                instance.distance_mat[last_visit_task, task_id]
            if arrival_time < task.ready_time:
                current_time = task.ready_time + task.service_time
            elif arrival_time > task.due_time:
                violation += (arrival_time - task.due_time)
                current_time = arrival_time + task.service_time
            else:
                current_time = arrival_time + task.service_time
            last_visit_task = task_id

            if violation > 0.3 * instance.average_time_window_width:
                # 如果时间窗违约量太大，直接返回一个很大的数，表示这个解不可行
                return int(1e9)

        return violation

    @staticmethod
    def check_pickup_before_delivery(route: list[int], instance: ProblemInstance) -> bool:
        """
        检查一条路线是否满足先取后送约束
        """
        vis = set()
        for task_id in route:
            task = instance.tasks[task_id]
            if task.pickup > 0 and (task.pickup not in vis):
                return False
            vis.add(task_id)

        return True

    @staticmethod
    def check_pickup_before_delivery_for_solution(solution: 'Solution') -> bool:
        """
        检查一个解是否满足先取后送约束
        """
        instance = solution.instance
        for route in solution.routes:
            if not FeasibilityChecker.check_pickup_before_delivery(route, instance):
                return False
        return True


class CostEvaluator:

    @staticmethod
    def route_cost(route: list[int], instance: ProblemInstance) -> float:
        """
        计算一条路线的距离成本
        """
        last_task_id = 0
        cost = 0.0
        for task_id in route:
            cost += instance.distance_mat[last_task_id, task_id]
            last_task_id = task_id
        cost += instance.distance_mat[last_task_id, 0]
        return cost

    @staticmethod
    def distance_cost(solution: 'Solution') -> float:
        """
        计算一个解的总距离成本
        """
        instance = solution.instance
        total_cost = 0.0
        for route in solution.routes:
            total_cost += CostEvaluator.route_cost(route, instance)
        return total_cost

    @staticmethod
    def calculate_capacity_violation(solution: 'Solution') -> float:
        """
        计算一个解的总容量违约量
        """
        total_violation = 0.0
        instance = solution.instance
        for route in solution.routes:
            violation = FeasibilityChecker.calculate_capacity_violation(
                route, instance)
            total_violation += violation
        return total_violation

    @staticmethod
    def calculate_time_window_violation(solution: 'Solution') -> float:
        """
        计算一个解的总时间窗违约量
        """
        instance = solution.instance
        total_violation = 0.0
        for route in solution.routes:
            violation = FeasibilityChecker.calculate_time_window_violation(
                route, instance)
            total_violation += violation
        return total_violation
