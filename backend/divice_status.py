import psutil
import time
from typing import Dict, Any


psutil.cpu_percent(interval=None)

def get_boot_time() -> Dict[str, Any]:
    """
    获取系统开机时间
    :return: dict 包含开机时间和已运行时间的详细信息
    """
    # 1. 获取开机时间的时间戳（自 1970年以来的秒数）
    boot_time = psutil.boot_time()

    # 2. 获取当前时间的时间戳
    current_time = time.time()

    # 3. 计算已运行的秒数
    uptime_seconds = current_time - boot_time

    # 4. 把干瘪的秒数，转换成人类易读的 小时、分钟、秒
    hours = int(uptime_seconds // 3600)
    minutes = int((uptime_seconds % 3600) // 60)
    seconds = int(uptime_seconds % 60)

    # print(f"💻 系统已连续运行: {hours} 小时 {minutes} 分钟 {seconds} 秒")
    return {
        "boot_time": boot_time,
        "uptime_seconds": uptime_seconds,
        "hours": hours,
        "minutes": minutes,
        "seconds": seconds
    }


def get_cpu_usage() -> float:
    """
    获取 CPU 使用率
    :return: float CPU 使用率百分比
    """
    cpu_usage = psutil.cpu_percent(interval=None)
    return cpu_usage


def get_memory_usage() -> Dict[str, Any]:
    """
    获取内存使用情况
    :return: dict 包含总内存、已用内存、可用内存和使用率的详细信息
    """
    memory_info = psutil.virtual_memory()
    total = memory_info.total / (1024 ** 3)  # 转换为 GB
    used = memory_info.used / (1024 ** 3)    # 转换为 GB
    return {
        "total": total,
        "used": used,
        "percent": memory_info.percent
    }


if __name__ == "__main__":
    boot_info = get_boot_time()
    print(f"⏱️ 系统开机时间: {boot_info['hours']:02d}:{boot_info['minutes']:02d}:{boot_info['seconds']:02d}")
    time.sleep(1)  # 等待一秒钟以获取准确的 CPU 使用率
    cpu_info = get_cpu_usage()
    print(f"💻 CPU 使用率: {cpu_info}%")