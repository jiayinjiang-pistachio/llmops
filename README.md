
# 创建虚拟环境
```bash
python3 -m venv env
```

# 激活虚拟环境（macos）
```bash
source env/bin/activate
```

# 退出当前虚拟环境
```bash
deactivate
```


# 生成 requirements.txt
```bash
# 安装相关依赖
pip install --no-deps pipreqs
pip install yarg==0.1.9 docopt==0.6.2

# 执行该命令生成
pipreqs --ignore env --force 
```

# 项目安装依赖
```bash
pip install -r requirements.txt
```


