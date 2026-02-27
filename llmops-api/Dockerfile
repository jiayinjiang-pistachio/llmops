# 方案：合并阶段 + 优化层缓存 + 清理冗余
FROM python:3.11-slim

# 1. 设置工作目录
WORKDIR /api

# 2. 设置环境变量 (保持不变)
ENV FLASK_APP=app/http/app.py \
    FLASK_ENV=production \
    FLASK_DEBUG=0 \
    NLTK_DATA=/api/internal/core/unstructured/nltk_data \
    TZ=Asia/Shanghai \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# 3. 安装系统依赖 (合并命令减少 Layer，安装完成后立即清理缓存)
RUN apt-get update && apt-get install -y --no-install-recommends \
    bash \
    && rm -rf /var/lib/apt/lists/*

# 4. 关键：利用缓存安装 Python 依赖
# 先 COPY requirements.txt，这样只要文件不变，这层就会被 Cached
COPY requirements.txt .

# 建议：如果不需要本地跑 GPU 模型，在安装前通过环境变量或镜像源提速
# --no-cache-dir 必须保留，防止 pip 缓存占用额外一倍的磁盘空间
RUN pip install --no-cache-dir -r requirements.txt \
    -i https://pypi.tuna.tsinghua.edu.cn/simple

# 5. 拷贝源码 (最后拷贝源码，因为源码变动最频繁)
# 这里的 . 指的是 docker compose build 时指定的 context 目录
COPY . /api

# 6. 运行脚本处理
COPY docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 5001

ENTRYPOINT ["/bin/bash", "/entrypoint.sh"]