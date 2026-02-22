from dataclasses import dataclass


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

    # 请求列表，键为request id，值为(取货任务id, 送货任务id)
    requests_: dict[int, tuple[int, int]] = {}
    delivery_to_pickup_: dict[int, int] = {}  # 送货任务id到取货任务id的映射
    pickup_to_request_: dict[int, int] = {}  # 取货任务id到request id的映射
    delivery_to_request_: dict[int, int] = {}  # 送货任务id到request id的映射
    tasks_: dict[int, Task] = {}      # 键为任务id，值为Task对象
    distance_matrix_: dict[tuple[int, int], float] = {}   # 距离矩阵，键为任务id对，值为距离

    number_of_vehicles_: int = 0
    vehicle_capacity_: int = 0
    depot_x_: int = 0
    depot_y_: int = 0
