# 1. 使用轻量级的 Python 官方镜像
FROM python:3.11-slim

# 2. 设置环境变量
# PYTHONUNBUFFERED 保证 Python 产生的日志能立即发送到 Cloud Logging，不会被缓存
ENV PYTHONUNBUFFERED True
# 定义工作目录
ENV APP_HOME /app
WORKDIR $APP_HOME

# 3. 首先只复制依赖文件（利用 Docker 层的缓存机制）
# 只要 requirements.txt 没变，下次构建就会直接跳过 pip install 步骤，极速打包
COPY requirements.txt .

# 4. 安装依赖
RUN pip install --no-cache-dir -r requirements.txt

# 5. 将当前目录下的所有代码复制到容器中
COPY . .

# 6. 启动服务
# Cloud Run 会自动注入 $PORT 环境变量（默认为 8080）
# 使用 exec 模式启动可以让容器更好地接收来自 GCP 的终止信号，实现平滑关闭
CMD exec uvicorn main:app --host 0.0.0.0 --port $PORT
