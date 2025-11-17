from mcp.server.fastmcp import FastMCP

# 创建 MCP 服务器
mcp = FastMCP(name="Demo",
    port=8400,
    host="0.0.0.0"
    )

# 添加工具 - 两数相加
@mcp.tool(name="add", description="两数相加")
def add(a: int, b: int) -> int:
    return a + b + 100

# 添加工具 - 两数相乘
@mcp.tool(name="multiply", description="两数相乘")
def multiply(a: int, b: int) -> int:
    return a * b

if __name__ == "__main__":
    mcp.run(transport="sse")
