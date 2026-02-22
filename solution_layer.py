from dataclasses import dataclass


@dataclass(slots=True)
class Solution:
    routes_: list[list[int]]  # 所有车辆路线
    request_bank_: list[int]  # 未分配的请求ID列表
    solution_cost_: float = 0.0  # 总距离成本
    vehicle_count_: int = 0  # 使用的车辆数量

    def copy(self) -> "Solution":
        new_routes = []
        for route in self.routes_:
            new_routes.append(list(route))

        return Solution(
            routes_=new_routes,
            request_bank_=list(self.request_bank_),
            solution_cost_=self.solution_cost_,
            vehicle_count_=self.vehicle_count_
        )
