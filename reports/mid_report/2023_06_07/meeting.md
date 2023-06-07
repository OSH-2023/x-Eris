# 2023_06_07 会议记录
## Lab4 
本次会议主要决定了计算任务选为蒙特卡洛法计算$e$，具体算法可参见代码，并且尝试了Ray Cluster的部署连接等操作。

Docker 部署相关文档草稿置于此处。

> 请确保所有设备处于同一局域网内

### 安装 Docker
1. 安装 Docker Desktop: [docker.com](https://www.docker.com/)

2. 下载 Ray 的 Dockeer 镜像

```bash
(amd64) docker pull rayproject/ray

(aarm64) docker pull rayproject/ray:nightly-aarch64
```

3. 运行 Docker

```bash
(amd64) docker run --shm-size=1gb -m 2g -t --tty --interactive -p 8888:8888 -p 6379:6379 rayproject/ray

(aarm64) docker run --shm-size=2.32gb -m 2g -t --tty --interactive -p 8888:8888 -p 6379:6379 rayproject/ray:nightly-aarch64
```

### 启动 Ray
1. 启动头节点
```bash
(docker) ray start  --head  --dashboard-host=0.0.0.0 --dashboard-port=8888
```
此时可于宿主机浏览器中访问 `localhost:8888` 查看 ```Ray Dashboard```

2. 启动工作节点（可以在宿主机，也可以在同一局域网任意设备/设备之上 Docker 容器内）并连接至集群
```bash
(docker) ray start --address='172.17.0.2:6379'
```

4. 通过 Docker Desktop 将脚本文件复制进容器中，推荐放置在 `/home/ray` 目录下，这是进入容器后的默认位置。

3. 开始计算
```bash
(docker) RAY_DEDUP_LOGS=0 python e.py
```


## Log
```
1 docker 1250000 3.316246747970581
2 docker 1250000 3.115318775177002
```

## 计划
本周末前完成单机部署以及分布式部署文档编写，以及单机性能优化相关分析。

完成之后约定下一次会议时间，讨论 Lab4 报告编写以及 EFS 融合调试。