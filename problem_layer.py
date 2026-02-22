from dataclasses import dataclass

@dataclass(slots=True)
class Task:
    id_: int   # 取送任务的唯一标识符
    x_: int
    y_: int  # 坐标
    demand_: int   # 负数表示送货，正数表示取货
    ready_time_: int
    due_time_: int   # 时间窗
    service_time_: int   # 服务时间
    _pickup: int
    delivery_: int


@dataclass(slots=True)
class Request:
    _request_id: int  # 请求的唯一标识符
    _pickup_task_id: int   # 取货任务的id
    _delivery_task_id: int  # 送货任务的id


@dataclass(slots=True)
class Vehicle:
    _vehicle_id: int  # 车辆的唯一标识符


@dataclass(slots=True)
class ProblemInstance:

    requests_: dict[int, int]   # 请求列表，键为取货任务id，值为送货任务id
    delivery_to_pickup_: dict[int, int]
    tasks_: dict[int, Task]      # 取送任务列表
    distance_matrix_: dict[tuple[int, int], float]   # 距离矩阵，键为任务id对，值为距离

    number_of_vehicles_: int = 0
    vehicle_capacity_: int = 0
    depot_x_: int = 0
    depot_y_: int = 0
