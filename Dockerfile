FROM python:3.10-slim

WORKDIR /app

# 复制项目文件
COPY . .

# 安装依赖
RUN pip install --no-cache-dir -e .

# 暴露端口（如果需要）
# EXPOSE 8000

# 启动 MCP 服务
CMD ["python", "-m", "ssq_mcp"]
