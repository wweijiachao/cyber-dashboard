import asyncio
import websockets
import json
from divice_status import get_boot_time, get_cpu_usage, get_memory_usage

async def handle_connection(websocket):
    """
    处理每一个连接进来的客户端
    """
    print(f"客户端已连接: {websocket.remote_address}")

    try:
        while True:
            # 获取系统状态信息
            boot_info = get_boot_time()
            boot_time = f"{boot_info['hours']:02d}:{boot_info['minutes']:02d}:{boot_info['seconds']:02d}"
            cpu_usage = get_cpu_usage()
            memory_info = get_memory_usage()

            # 构建要发给前端的数据
            payload = {
                "boot_time": boot_time,
                "cpu_usage": cpu_usage,
                "memory_total": memory_info["total"],
                "memory_used": memory_info["used"],
                "memory_percent": memory_info["percent"]
            }
            # 将数据转换为 JSON 格式
            json_data = json.dumps(payload)
            # 发送数据给前端
            await websocket.send(json_data)
            # 异步休眠，每隔 1 秒发送一次数据
            await asyncio.sleep(1)
    except websockets.exceptions.ConnectionClosed:
        # 客户端断开连接时的处理
        print(f"客户端已断开连接: {websocket.remote_address}")


async def main():
    """
    启动 WebSocket 服务器
    """
    async with websockets.serve(handle_connection, "localhost", 8765):
        print("WebSocket 服务器已启动，监听端口 8765")
        await asyncio.Future()  # 保持服务器运行，main函数永远挂起，不会结束


if __name__ == "__main__":
    # 启动事件循环，运行 WebSocket 服务器
    asyncio.run(main())
            
