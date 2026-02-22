from solution_layer import Route, Solution
from problem_layer import ProblemInstance


class FeasibilityChecker:
    def check_route(self, route: Route, instance: ProblemInstance) -> bool:
        return self.check_capacity(route, instance) and self.check_time_windows(route, instance) and self.check_pickup_before_delivery(route, instance)

    @staticmethod
    def check_capacity(route: Route, instance: ProblemInstance) -> bool:
        current_load = 0
        for task_id in route.visit_tasks_:
            task = instance.tasks_[task_id]
            current_load += task.demand_
            if current_load > instance.vehicle_capacity_:
                return False

        return True

    @staticmethod
    def check_time_windows(route: Route, instance: ProblemInstance) -> bool:
        current_time = 0
        last_visit_task = 0
        for task_id in route.visit_tasks_:
            task = instance.tasks_[task_id]
            arrival_time = current_time + \
                instance.distance_matrix_[(last_visit_task, task_id)]
            if arrival_time < task.ready_time_:
                current_time = task.ready_time_ + task.service_time_
            elif arrival_time > task.due_time_:
                return False
            else:
                current_time = arrival_time + task.service_time_

        return True

    def check_pickup_before_delivery(self, route: Route, instance: ProblemInstance) -> bool:
        pass


class CostEvaluator:
    def route_cost(self, route: Route) -> float:
        pass

    def solution_cost(self, solution: Solution) -> float:
        pass
