#!/bin/bash

# 启用错误检查：任何命令失败即退出脚本
set -e

# 1. 判断是否启用数据库迁移同步
if [[ "${MIGRATION_ENABLED}" == "true" ]]; then
  echo ">>> Running database migrations..."
  # 建议使用 flask db upgrade 而不是完整的路径，只要 FLASK_APP 已设置
  flask --app app.http.app db upgrade
fi

# 2. 检测运行模式 (MODE)
if [[ "${MODE}" == "celery" ]]; then
  echo ">>> Starting Celery Worker (Mode: ${CELERY_WORKER_CLASS:-prefork})..."
  # 使用 exec 确保信号传递
  exec celery -A app.http.app.celery worker \
    -P ${CELERY_WORKER_CLASS:-prefork} \
    -c ${CELERY_WORKER_AMOUNT:-5} \
    --loglevel INFO
else
  # 3. API 启动逻辑
  if [[ "${FLASK_ENV}" == "development" ]]; then
    echo ">>> Starting Flask Development Server..."
    # 明确告诉 flask 入口文件在哪里
    exec flask --app app.http.app run --host=${LLMOPS_BIND_ADDRESS:-0.0.0.0} --port=${LLMOPS_PORT:-5000} --debug
  else
    echo ">>> Starting Gunicorn Production Server..."
    # 修正了 SERVER_WORKER_AMOUNT 的拼写
    exec gunicorn \
      --bind "${LLMOPS_BIND_ADDRESS:-0.0.0.0}:${LLMOPS_PORT:-5001}" \
      --workers ${SERVER_WORKER_AMOUNT:-1} \
      --worker-class ${SERVER_WORKER_CLASS:-gthread} \
      --threads ${SERVER_THREAD_AMOUNT:-2} \
      --timeout ${GUNICORN_TIMEOUT:-600} \
      --preload \
      --access-logfile - \
      --error-logfile - \
      app.http.app:app
  fi
fi