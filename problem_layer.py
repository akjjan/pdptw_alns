from dataclasses import dataclass, field
import numpy as np


@dataclass(slots=True)
class Task:
    x: int
    y: int  # 坐标
    demand: int  # 负数表示送货，正数表示取货
    ready_time: int
    due_time: int  # 时间窗
    service_time: int  # 服务时间
    pickup: int
    delivery: int


@dataclass(slots=True)
class ProblemInstance:
    # 键: request id，值: (取货任务id, 送货任务id)
    requests: dict[int, tuple[int, int]] = field(default_factory=dict)
    delivery_to_pickup: dict[int, int] = field(
        default_factory=dict)  # 送货任务id到取货任务id的映射
    pickup_to_request: dict[int, int] = field(
        default_factory=dict)  # 取货任务id到request id的映射
    delivery_to_request: dict[int, int] = field(
        default_factory=dict)  # 送货任务id到request id的映射
    tasks: dict[int, Task] = field(
        default_factory=dict)  # 键:任务id，值为Task对象
    distance_mat: np.ndarray = field(
        default_factory=lambda: np.array([]))  # 距离数组

    number_of_vehicles: int = 0
    vehicle_capacity: int = 0
    depot_x: int = 0
    depot_y: int = 0

    max_distance: float = 0.0
    average_time_window_width: float = 0.0
    half_capacity: float = 0.0
