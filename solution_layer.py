from dataclasses import dataclass


@dataclass(slots=True)
class Route:
    visit_tasks_: list[int]  # 车辆行驶的节点序列，包含起始点和结束点


@dataclass(slots=True)
class Solution:
    _routes: list[Route]  # 所有车辆路线
    _unassigned_requests: list[int]  # 未分配的请求ID列表
    _total_cost: float = 0.0  # 总成本

    def copy(self) -> "Solution":
        new_routes = []
        for route in self._routes:
            new_route = Route(
                visit_tasks_=list(route.visit_tasks_)       # 复制列表
            )
            new_routes.append(new_route)

        return Solution(
            _routes=new_routes,
            _unassigned_requests=list(self._unassigned_requests),
            _total_cost=self._total_cost
        )
