<div align="center">

<img src="https://img.shields.io/badge/-API2MCP-000000?style=for-the-badge&labelColor=faf9f6&color=faf9f6&logoColor=000000" alt="API2MCP" width="320"/>

<h4>Transform Your APIs into MCP Tools Effortlessly</h4>

**English** | [简体中文](README-CN.md)

<a href="https://github.com/yourusername/API2MCP">
  <img alt="GitHub version" src="https://img.shields.io/badge/version-0.0.1-blue.svg?style=for-the-badge" />
</a>
<a href="LICENSE">
  <img alt="License MIT" src="https://img.shields.io/badge/License-MIT-blue.svg?style=for-the-badge" />
</a>

</div>

API2MCP is a lightweight framework that enables you to quickly build MCP (Model Context Protocol) servers. Transform your existing APIs into AI-accessible tools with minimal code.

## Table of Contents
- [Table of Contents](#table-of-contents)
- [Why API2MCP?](#why-api2mcp)
  - [Core Features](#core-features)
  - [Key Capabilities](#key-capabilities)
- [Technology Stack](#technology-stack)
- [Quick Start](#quick-start)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Development](#development)
- [Project Structure](#project-structure)
- [Usage](#usage)
  - [Creating MCP Tools](#creating-mcp-tools)
  - [Running the Server](#running-the-server)
  - [Docker Deployment](#docker-deployment)
- [Configuration](#configuration)
- [Examples](#examples)
- [Contributing](#contributing)
- [License](#license)

## Why API2MCP?

API2MCP bridges the gap between traditional APIs and AI systems by exposing your functions as MCP tools that can be discovered and used by AI assistants like Claude.

### Core Features

**🚀 Simple & Fast**
- Decorator-based tool registration
- Automatic type inference and validation
- Zero boilerplate code required
- Built on FastMCP for optimal performance

**🔌 Flexible Integration**
- Support for SSE (Server-Sent Events) transport
- Works with any Python function
- Easy to extend with custom tools
- Compatible with existing Python codebases

**🐳 Production Ready**
- Docker support out of the box
- Docker Compose for easy deployment
- Configurable host and port settings
- Health checks and monitoring support

### Key Capabilities

- **Declarative API**: Define tools with simple decorators
- **Type Safety**: Automatic parameter validation using Python type hints
- **Hot Reload**: Development mode with automatic reloading
- **Scalable**: Asynchronous execution with SSE transport
- **Extensible**: Easy to add new tools and integrate with existing systems

## Technology Stack

**Backend:**
- **[FastMCP](https://github.com/jlowin/fastmcp)**: High-performance MCP server framework
- **Python 3.11+**: Modern Python with type hints
- **SSE Transport**: Server-Sent Events for real-time communication

**DevOps:**
- **Docker**: Containerized deployment
- **Docker Compose**: Multi-container orchestration

## Quick Start

### Prerequisites

- **Python**: 3.11 or higher
- **pip**: Latest version
- **Docker** (optional): For containerized deployment

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/API2MCP.git
cd API2MCP

# Install dependencies
pip install -r requirements.txt
```

### Development

**Run the MCP Server Locally:**

```bash
python src/main.py
```

The server will start on `http://0.0.0.0:8400` with SSE transport enabled.

**Test the Tools:**

Once running, your MCP tools will be available for AI assistants to discover and use. The current demo includes:
- `add`: Add two numbers together
- `multiply`: Multiply two numbers

## Project Structure

```
API2MCP/
├── src/
│   └── main.py              # MCP server entry point
├── docker/
│   ├── Dockerfile           # Docker image definition
│   └── docker-compose.yml   # Docker Compose configuration
├── requirements.txt         # Python dependencies
├── .gitignore              # Git ignore rules
└── README.md               # This file
```

## Usage

### Creating MCP Tools

Define your tools using the `@mcp.tool()` decorator:

```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP(name="MyServer", port=8400, host="0.0.0.0")

@mcp.tool(name="my_tool", description="Description of what this tool does")
def my_tool(param1: str, param2: int) -> dict:
    """
    Your tool implementation here
    """
    return {"result": f"Processed {param1} with {param2}"}
```

**Best Practices:**
- Use clear, descriptive names for your tools
- Provide detailed descriptions for AI understanding
- Use Python type hints for automatic validation
- Return structured data (dict, list, etc.) when possible

### Running the Server

**Local Development:**

```python
if __name__ == "__main__":
    mcp.run(transport="sse")
```

**Configuration Options:**

```python
mcp = FastMCP(
    name="MyServer",      # Server name
    port=8400,            # Port number
    host="0.0.0.0"        # Host address (0.0.0.0 for all interfaces)
)
```

### Docker Deployment

**Build and Run with Docker:**

```bash
# Build the image
docker build -f docker/Dockerfile -t api2mcp .

# Run the container
docker run -p 8400:8400 api2mcp
```

**Using Docker Compose:**

```bash
# Start the service
docker-compose -f docker/docker-compose.yml up -d

# View logs
docker-compose -f docker/docker-compose.yml logs -f

# Stop the service
docker-compose -f docker/docker-compose.yml down
```

The Docker Compose setup includes:
- Automatic restarts (`unless-stopped`)
- Port mapping (8400:8400)
- Linux/AMD64 platform support

## Configuration

**Environment Variables:**

You can customize the server behavior using environment variables:

```bash
# Server configuration
MCP_SERVER_NAME=MyServer
MCP_SERVER_PORT=8400
MCP_SERVER_HOST=0.0.0.0

# Transport settings
MCP_TRANSPORT=sse
```

**In Code:**

```python
import os

mcp = FastMCP(
    name=os.getenv("MCP_SERVER_NAME", "Demo"),
    port=int(os.getenv("MCP_SERVER_PORT", 8400)),
    host=os.getenv("MCP_SERVER_HOST", "0.0.0.0")
)
```

## Examples

### Example 1: Math Operations

```python
@mcp.tool(name="add", description="Add two numbers")
def add(a: int, b: int) -> int:
    return a + b

@mcp.tool(name="multiply", description="Multiply two numbers")
def multiply(a: int, b: int) -> int:
    return a * b
```

### Example 2: String Processing

```python
@mcp.tool(name="format_text", description="Format text with various options")
def format_text(text: str, uppercase: bool = False, trim: bool = True) -> str:
    result = text.strip() if trim else text
    return result.upper() if uppercase else result
```

### Example 3: Data Retrieval

```python
@mcp.tool(name="get_user_info", description="Retrieve user information")
def get_user_info(user_id: int) -> dict:
    # Your logic here
    return {
        "user_id": user_id,
        "name": "John Doe",
        "email": "john@example.com"
    }
```

### Example 4: Weather Information (with API Integration)

```python
import requests
from typing import Dict, Any

@mcp.tool(name="get_weather", description="获取指定城市的天气信息，支持中文和英文城市名")
def get_weather(city: str, lang: str = "zh") -> Dict[str, Any]:
    """
    获取指定城市的天气信息
    
    Args:
        city: 城市名称，例如 "北京", "Shanghai", "New York"
        lang: 语言设置，默认为 "zh" (中文)，可选 "en" (英文)
    
    Returns:
        包含天气信息的字典，包括温度、天气状况、湿度、风速等
    """
    try:
        format_str = "%C+%t+%h+%w+%l"
        url = f"https://wttr.in/{city}?format={format_str}&lang={lang}"
        
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        data = response.text.strip().split()
        
        if len(data) >= 4:
            return {
                "success": True,
                "city": city,
                "condition": data[0],      # 天气状况
                "temperature": data[1],    # 温度
                "humidity": data[2],       # 湿度
                "wind_speed": data[3],     # 风速
                "location": " ".join(data[4:]) if len(data) > 4 else city,
                "raw_data": response.text.strip()
            }
        else:
            return {
                "success": False,
                "city": city,
                "error": "无法解析天气数据"
            }
            
    except Exception as e:
        return {
            "success": False,
            "city": city,
            "error": f"发生错误: {str(e)}"
        }
```

**Usage:**
```python
# 查询北京天气（中文）
result = get_weather("北京")
# 返回: {"success": True, "city": "北京", "condition": "晴", "temperature": "+15°C", ...}

# 查询纽约天气（英文）
result = get_weather("New York", lang="en")
# 返回: {"success": True, "city": "New York", "condition": "Clear", "temperature": "+59°F", ...}
```

## Contributing

We welcome contributions! Please follow these guidelines:

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Follow** the coding style:
   - Use type hints for all function parameters and returns
   - Write clear docstrings for tools
   - Follow PEP 8 style guidelines
4. **Test** your changes thoroughly
5. **Commit** with conventional commits (`feat:`, `fix:`, `docs:`, etc.)
6. **Push** and open a Pull Request

**Development Tips:**
- Test your tools with an MCP client before committing
- Use meaningful tool names and descriptions
- Document any new configuration options
- Update the README with new examples

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

<div align="center">

Made with ❤️ by the API2MCP Community

**Star ⭐ this repo if you find it useful!**

</div>
