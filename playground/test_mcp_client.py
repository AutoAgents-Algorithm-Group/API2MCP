"""
MCP Client 测试脚本 - 使用 langchain-mcp-adapters

使用方法:
1. 先启动 MCP Server: python -m src.api.main
2. 运行此测试脚本: python playground/test_mcp_client.py
"""
import asyncio
import os
import time

from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent


# MCP 服务器配置
MCP_SERVER_URL = os.getenv("MCP_SERVER_URL", "http://localhost:9090/sse")
SERVER_NAME = "outage_mcp"


async def test_list_tools(timeout: int = 10):
    """测试列出所有可用工具"""
    print("=" * 60)
    print("测试 1: 列出所有可用工具")
    print("=" * 60)
    
    print(f"\n🔍 连接服务器: {SERVER_NAME}")
    print(f"   URL: {MCP_SERVER_URL}")
    
    try:
        start_time = time.time()
        
        client = MultiServerMCPClient({
            SERVER_NAME: {
                "url": MCP_SERVER_URL,
                "transport": "sse",
            }
        })
        
        tools = await asyncio.wait_for(client.get_tools(), timeout=timeout)
        
        elapsed = time.time() - start_time
        
        print(f"\n✅ 连接成功 ({elapsed:.2f}秒)")
        print(f"📦 找到 {len(tools)} 个工具:")
        
        for i, tool in enumerate(tools, 1):
            name = tool.name if hasattr(tool, 'name') else str(tool)
            desc = tool.description[:50] if hasattr(tool, 'description') else ""
            print(f"  {i}. {name}: {desc}...")
        
        return tools
        
    except asyncio.TimeoutError:
        print(f"\n⏱️ 连接超时 (>{timeout}秒)")
        return []
    except Exception as e:
        print(f"\n❌ 连接失败: {e}")
        raise


async def test_call_tool_directly(timeout: int = 15):
    """测试直接调用工具"""
    print("\n" + "=" * 60)
    print("测试 2: 直接调用工具")
    print("=" * 60)
    
    try:
        client = MultiServerMCPClient({
            SERVER_NAME: {
                "url": MCP_SERVER_URL,
                "transport": "sse",
            }
        })
        
        tools = await asyncio.wait_for(client.get_tools(), timeout=timeout)
        
        # 查找 get_event_data 工具
        get_event_tool = next(
            (t for t in tools if hasattr(t, 'name') and t.name == "get_event_data"), 
            None
        )
        
        if get_event_tool:
            print(f"\n调用工具: {get_event_tool.name}")
            try:
                result = await asyncio.wait_for(
                    get_event_tool.ainvoke({"outage_number": "TEST-001"}),
                    timeout=timeout
                )
                print(f"结果: {result}")
            except asyncio.TimeoutError:
                print("调用超时")
            except Exception as e:
                print(f"调用失败（预期，因为后端服务可能不可用）: {e}")
        else:
            print(f"\n未找到 get_event_data 工具")
            print(f"可用工具: {[t.name for t in tools if hasattr(t, 'name')]}")
            
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")


async def test_with_agent(timeout: int = 30):
    """测试与 LangChain Agent 集成"""
    print("\n" + "=" * 60)
    print("测试 3: 与 LangChain Agent 集成")
    print("=" * 60)
    
    # 检查 OpenAI API Key
    if not os.getenv("OPENAI_API_KEY"):
        print("\n跳过: 未设置 OPENAI_API_KEY 环境变量")
        return
    
    try:
        client = MultiServerMCPClient({
            SERVER_NAME: {
                "url": MCP_SERVER_URL,
                "transport": "sse",
            }
        })
        
        tools = await asyncio.wait_for(client.get_tools(), timeout=timeout)
        
        # 创建 LLM
        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
        
        # 创建 Agent
        agent = create_react_agent(llm, tools)
        
        # 测试 Agent
        print("\n询问 Agent: 你有哪些可用的工具?")
        response = await asyncio.wait_for(
            agent.ainvoke({
                "messages": [{"role": "user", "content": "你有哪些可用的工具? 请列出它们的名称和用途。"}]
            }),
            timeout=timeout
        )
        
        # 输出最后的 AI 消息
        for msg in reversed(response["messages"]):
            if hasattr(msg, "content") and msg.content:
                print(f"\nAgent 回复:\n{msg.content}")
                break
                
    except asyncio.TimeoutError:
        print("\n⏱️ Agent 调用超时")
    except Exception as e:
        print(f"\n❌ Agent 测试失败: {e}")


async def main():
    """运行所有测试"""
    print("\n🚀 开始 MCP Client 测试")
    print(f"📡 MCP Server URL: {MCP_SERVER_URL}")
    print("\n请确保 MCP Server 已启动: python -m src.api.main\n")
    
    try:
        # 测试 1: 列出工具
        tools = await test_list_tools()
        
        if not tools:
            print("\n❌ 无法获取工具列表，跳过后续测试")
            return
        
        # 测试 2: 直接调用工具
        await test_call_tool_directly()
        
        # 测试 3: Agent 集成（需要 OpenAI API Key）
        # await test_with_agent()
        
        print("\n" + "=" * 60)
        print("✅ 测试完成!")
        print("=" * 60)
        
    except ConnectionError as e:
        print(f"\n❌ 连接失败: {e}")
        print("请确保 MCP Server 已启动: python -m src.api.main")
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
