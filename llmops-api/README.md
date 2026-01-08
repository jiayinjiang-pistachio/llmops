# 从已有的安装依赖中生成requirements.txt

`pip freeze > requirements.txt`

`pip install -r requirements.txt`

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

# 解决端口占用问题

```
sudo kill -9 PIP_ID
```

# conda 创建虚拟环境

```bash
# 查看现有环境
conda info --envs 

# 移除环境
env remove -n llmops_v6_py3.10

# 创建
 conda create -n llmops_v6_py3.10 python=3.10
```

# 端口占用

```
# 在终端执行：
# 1. 查找占用端口 5000 的进程
sudo lsof -i :5000

# 2. 找到 PID（进程ID），然后杀死
kill -9 <PID>

# 或者一步完成
sudo kill -9 $(sudo lsof -t -i:5000)
```