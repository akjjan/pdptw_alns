from dataclasses import dataclass
from typing import Optional


@dataclass(slots=True)
class Task:
    _id: int   # 取送任务的唯一标识符
    _x: int
    _y: int  # 坐标
    _demand: int   # 负数表示送货，正数表示取货
    _ready_time: int
    _due_time: int   # 时间窗
    _service_time: int   # 服务时间
    _pickup: int
    _delivery: int


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

    _vehicles: list[Vehicle]  # 车辆列表
    _requests: dict[int, int]   # 请求列表，键为取货任务id，值为送货任务id
    _tasks: dict[int, Task]      # 取送任务列表
    _distance_matrix: dict[tuple[int, int], float]   # 距离矩阵，键为任务id对，值为距离

    _number_of_vehicles: int = 0
    _vehicle_capacity: int = 0
    _depot_x: int = 0
    _depot_y: int = 0
