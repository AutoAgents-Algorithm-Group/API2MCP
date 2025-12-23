"""
简单的 MCP Client 测试脚本 - 使用 mcp 官方 SDK

使用方法:
1. 先启动 MCP Server: python -m src.api.main
2. 运行此测试脚本: python playground/test_mcp_simple.py
"""
import asyncio
import httpx


MCP_SERVER_URL = "http://localhost:9090"


async def test_sse_connection():
    """测试 SSE 连接"""
    print("=" * 60)
    print("测试: SSE 连接")
    print("=" * 60)
    
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            async with client.stream("GET", f"{MCP_SERVER_URL}/sse") as response:
                print(f"状态码: {response.status_code}")
                print(f"Content-Type: {response.headers.get('content-type')}")
                
                # 读取前几个事件
                count = 0
                async for line in response.aiter_lines():
                    print(f"  收到: {line}")
                    count += 1
                    if count >= 5:
                        break
                        
                print("✅ SSE 连接成功!")
                
    except httpx.ConnectError:
        print("❌ 连接失败 - MCP Server 未启动")
        print("请先运行: python -m src.api.main")
    except Exception as e:
        print(f"❌ 错误: {e}")


async def main():
    print("\n🚀 MCP Server 简单连接测试")
    print(f"📡 Server URL: {MCP_SERVER_URL}\n")
    
    await test_sse_connection()


if __name__ == "__main__":
    asyncio.run(main())

