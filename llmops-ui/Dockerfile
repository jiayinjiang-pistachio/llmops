# 第一阶段：编译阶段
FROM node:20-slim AS build-stage

# 安装 pnpm
ENV PNPM_HOME="/pnpm"
ENV PATH="$PNPM_HOME:$PATH"
RUN corepack enable

WORKDIR /app

# 先拷贝包管理文件，利用 Docker 缓存机制减少安装时间
COPY package.json pnpm-lock.yaml ./
RUN pnpm install --frozen-lockfile

# 拷贝源码并打包
COPY . .
RUN pnpm run build

# 第二阶段：运行阶段
FROM nginx:stable-alpine AS production-stage

# 拷贝打包后的静态文件到 Nginx 目录
COPY --from=build-stage /app/dist /usr/share/nginx/html

# 拷贝自定义的 Nginx 配置（覆盖默认配置）
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]