# 从已有的安装依赖中生成requirements.txt

`pip freeze > requirements.txt`

# 固定版本

```bash
 pip install langchain-core==0.2.5 langchain-huggingface==0.0.3 langchain-openai==0.1.8 langchain-text-splitters==0.2.1 langsmith==0.1.75 langchain==0.2.1 langchain-community==0.2.1 openai==1.109.1 tiktoken==0.12.0 

 pip install langchain-core==0.2.5 langchain-huggingface==0.0.3 langchain-text-splitters==0.2.1 langsmith==0.1.75 langchain==0.2.1 langchain-community==0.2.1 doctran==0.0.14

```

# docker 安装redis

```bash
# 拉取镜像
docker pull redis

# 运行 redis容器
docker run --name redis-dev -d -p 6379:6379 redis

# 在docker中连接 redis:
docker exec -it redis-dev redis-cli

# 启动容器
docker start redis-dev

# 停止容器
docker stop redis-dev
```
