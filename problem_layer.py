from dataclasses import dataclass, field
import numpy as np


@dataclass(slots=True)
class Task:
    x_: int
    y_: int  # 坐标
    demand_: int   # 负数表示送货，正数表示取货
    ready_time_: int
    due_time_: int   # 时间窗
    service_time_: int   # 服务时间
    pickup_: int
    delivery_: int


@dataclass(slots=True)
class ProblemInstance:

    # 键: request id，值: (取货任务id, 送货任务id)
    requests_: dict[int, tuple[int, int]] = field(default_factory=dict)
    delivery_to_pickup_: dict[int, int] = field(
        default_factory=dict)  # 送货任务id到取货任务id的映射
    pickup_to_request_: dict[int, int] = field(
        default_factory=dict)  # 取货任务id到request id的映射
    delivery_to_request_: dict[int, int] = field(
        default_factory=dict)  # 送货任务id到request id的映射
    tasks_: dict[int, Task] = field(
        default_factory=dict)      # 键:任务id，值为Task对象
    distance_matrix_: np.ndarray = field(
        default_factory=lambda: np.array([]))  # 距离矩阵

    number_of_vehicles_: int = 0
    vehicle_capacity_: int = 0
    depot_x_: int = 0
    depot_y_: int = 0

    max_distance_: float = 0.0
    average_time_window_width_: float = 0.0
    half_capacity_: float = 0.0
