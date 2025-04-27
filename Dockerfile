FROM python:3.10-slim

WORKDIR /app

# 复制项目文件
COPY . .

# 安装依赖
RUN pip install --no-cache-dir -e .

# 暴露健康检查端口
EXPOSE 8000

# 命令将由 smithery.yaml 中的 commandFunction 提供
