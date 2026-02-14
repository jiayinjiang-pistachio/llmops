# 第一阶段：构建阶段 (Builder)
FROM python:3.11-slim AS builder

WORKDIR /build

COPY requirements.txt .

# 使用缓存挂载安装依赖到指定目录
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --prefix=/pkg -r requirements.txt


# 第二阶段：生产环境 (Production)
FROM python:3.11-slim AS production

# 安装运行脚本所需的 bash
RUN apt-get update && apt-get install -y --no-install-recommends \
    bash \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /api

# 设置环境变量
ENV FLASK_APP=app/http/app.py \
    FLASK_ENV=production \
    FLASK_DEBUG=0 \
    NLTK_DATA=/api/internal/core/unstructured/nltk_data \
    TZ=Asia/Shanghai \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# 从构建阶段拷贝依赖
COPY --from=builder /pkg /usr/local
# 拷贝源码
COPY . /api

# 拷贝运行脚本并修正拼写错误
COPY docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 5001

ENTRYPOINT ["/bin/bash", "/entrypoint.sh"]