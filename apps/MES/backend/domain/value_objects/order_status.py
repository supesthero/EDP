from enum import Enum

class OrderStatus(str,Enum):
    """
    工单状态
    """

    PENDING = "PENDING" # 待处理
    IN_PROGRESS = "IN_PROGRESS" # 处理中
    COMPLETED = "COMPLETED" # 已完成
    CANCELLED = "CANCELLED" # 已取消
    FAILED = "FAILED" # 失败
    ON_HOLD = "ON_HOLD" # 暂停
    REOPENED = "REOPENED" # 重新打开