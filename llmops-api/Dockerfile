# 第一阶段：构建阶段 (Builder)
FROM python:3.11-slim AS builder

WORKDIR /build

# 安装编译所需的最小依赖 (针对 psycopg2-binary 之外的 C 扩展)
# 如果你已经改用了 psycopg2-binary，这步可以去掉以加速构建
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

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
    # 强制 Python 不生成 .pyc 缓存文件
    PYTHONDONTWRITEBYTECODE=1 \
    # 强制 Python 实时打印日志而不缓冲，方便 docker logs 查看
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