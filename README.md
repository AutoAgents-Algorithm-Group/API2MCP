<div align="center">

<img src="https://img.shields.io/badge/-API2MCP-000000?style=for-the-badge&labelColor=faf9f6&color=faf9f6&logoColor=000000" alt="API2MCP" width="320"/>

<h4>Transform Your APIs into MCP Tools Effortlessly</h4>


<a href="LICENSE">
  <img alt="License MIT" src="https://img.shields.io/badge/License-MIT-blue.svg?style=for-the-badge" />
</a>

</div>

API2MCP is a lightweight framework that enables you to quickly build MCP (Model Context Protocol) servers. Transform your existing APIs into AI-accessible tools with minimal code.

## Table of Contents
- [Why API2MCP?](#why-api2mcp)
- [Technology Stack](#technology-stack)
- [Quick Start](#quick-start)
- [Project Structure](#project-structure)
- [Docker Deployment](#docker-deployment)
- [Configuration](#configuration)
- [Testing](#testing)
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
- Health checks and monitoring
- Structured logging with Loguru

## Technology Stack

**Backend:**
- **[FastMCP](https://github.com/jlowin/fastmcp)**: High-performance MCP server framework
- **Python 3.11+**: Modern Python with type hints
- **Pydantic**: Data validation and settings management
- **Loguru**: Beautiful logging

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

### Run the Server

```bash
# Using Python directly
python -m src.api.main

# Or using Make
make dev
```

The server will start on `http://0.0.0.0:9090` with SSE transport enabled.

### Test the Connection

```bash
# Simple connection test
python playground/test_mcp_simple.py

# Full test with LangChain
python playground/test_mcp_client.py
```

## Project Structure

```
API2MCP/
├── src/
│   ├── __init__.py
│   ├── api/
│   │   ├── __init__.py
│   │   └── main.py              # MCP Server & tool definitions
│   ├── repository/
│   │   ├── __init__.py
│   │   └── constants.py         # Constants & mappings
│   ├── services/
│   │   ├── __init__.py
│   │   ├── data_service.py      # HTTP request utilities
│   │   ├── device_service.py    # Device data processing
│   │   ├── environment_service.py
│   │   ├── message_service.py
│   │   └── weather_service.py   # Weather data processing
│   └── utils/
│       ├── __init__.py
│       ├── config.py            # Configuration (Pydantic)
│       └── logger.py            # Logging (Loguru)
├── docker/
│   ├── Dockerfile
│   ├── docker-compose.yml
│   └── .dockerignore
├── playground/
│   ├── test.http                # HTTP test file
│   ├── test_mcp_simple.py       # Simple connection test
│   └── test_mcp_client.py       # LangChain MCP client test
├── Makefile                     # Common commands
├── requirements.txt
└── README.md
```

## Docker Deployment

### Using Docker Compose (Recommended)

```bash
# Build and start the service
make build
make run

# Or directly with docker-compose
docker-compose -f docker/docker-compose.yml up -d

# View logs
make logs

# Stop the service
make stop
```

### Using Docker Directly

```bash
# Build the image
docker build -f docker/Dockerfile -t api2mcp-server .

# Run the container
docker run -d \
  --name api2mcp-server \
  -p 9090:9090 \
  api2mcp-server
```

### Docker Configuration

The Docker setup includes:
- Health checks (every 30s)
- Automatic restarts (`unless-stopped`)
- Log rotation (10MB max, 3 files)
- Volume mounting for logs persistence

## Configuration

### Default Values (Hardcoded)

Configuration is managed in `src/utils/config.py` using Pydantic:

```python
class DataServiceConfig(BaseModel):
    # MCP Server
    mcp_host: str = "0.0.0.0"
    mcp_port: int = 9090
    
    # Data Service
    base_url: str = "http://25.91.83.60:18081"
    timeout: float = 10.0
    outage_token: str = "your-token"
    
    # Landform Service
    landform_url: str = "http://192.168.11.145:38000"
```

### Environment Variables (Docker)

You can override settings via environment variables in `docker-compose.yml`:

```yaml
environment:
  - MCP_HOST=0.0.0.0
  - MCP_PORT=9090
  - DATA_SERVICE_BASE_URL=http://your-service:8080
  - DATA_SERVICE_TIMEOUT=15
```

## Testing

### HTTP Testing (VS Code REST Client)

Use the `playground/test.http` file with VS Code REST Client extension:

```http
### SSE Connection Test
GET http://localhost:9090/sse
Accept: text/event-stream

### List Available Tools
POST http://localhost:9090/mcp
Content-Type: application/json

{
  "jsonrpc": "2.0",
  "method": "tools/list",
  "id": 1
}
```

### Python Testing

```bash
# Simple SSE connection test
python playground/test_mcp_simple.py

# Full test with LangChain MCP adapters
python playground/test_mcp_client.py
```

### LangChain Integration

```python
from langchain_mcp_adapters.client import MultiServerMCPClient

client = MultiServerMCPClient({
    "outage_mcp": {
        "url": "http://localhost:9090/sse",
        "transport": "sse",
    }
})

tools = await client.get_tools()
print(f"Found {len(tools)} tools")
```

## Available Tools

| Tool | Description |
|------|-------------|
| `get_event_data` | 获取停电事件基本信息 |
| `get_weather_data` | 获取停电时间沿线天气分析数据 |
| `weather_data_processing` | 处理并总结天气数据 |
| `work_order_query_tool` | 沿线诉求工单查询 |
| `get_environment_raw_data` | 获取原始环境数据 |
| `environment_data_processing` | 处理总结环境信息 |
| `get_drone_analysis` | 获取无人机图片分析结果 |
| `get_message_data` | 获取保护报文数据 |
| `get_wave_data` | 获取录波数据 |
| `message_data_processing` | 处理报文、录波数据 |
| `get_device_info_data` | 获取设备信息数据 |
| `process_device_info_data` | 处理设备信息数据 |

## Make Commands

```bash
make help      # Show available commands
make build     # Build Docker image
make run       # Start service (background)
make stop      # Stop service
make logs      # View logs
make clean     # Clean Docker resources
make dev       # Run in development mode
make test      # Run tests
make install   # Install dependencies
make restart   # Restart service
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

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

<div align="center">

Made with ❤️ by the API2MCP Community

**Star ⭐ this repo if you find it useful!**

</div>
