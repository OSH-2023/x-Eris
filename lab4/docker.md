# Ray
> 请确保所有设备处于同一局域网内

## 计算类测试任务
我们选取用蒙特卡洛法计算$e$来测试Ray的计算性能。

蒙特卡洛方法是一种用朴素模拟来计算近似值的方法，
具体来说，就是使用随机投点以及几何概型来计算$e$的值。

在这个问题里则是随机于 $[1, 2] \times [0,1]$ 的方格内随机投点，统计在
$y = 1/x$ 内外的点的个数。

同时，使用定积分可算出这一部分的面积为 $\ln 2$，即 $e^S = 2$，也就是$2^{1/S} = 2$，由此便可近似算出$e$。

具体的代码实现中总共模拟了$10^7$次投点过程，并计算$e$的近似值。

基础代码如下：  
```py
import time
import ray
import random


@ray.remote
def sum_remote(x):
    return sum(x)

# Actor class
@ray.remote
class monto(object):
    def __init__(self):
        self.c = 0
        self.n = 0
        # e = c/n
        self.e = 0.0

    def simulate(self, times):
        print("Begin to simulate for ", times, " times")
        self.n += times
        for i in range(times):
            x = random.uniform(1, 2)
            y = random.uniform(0, 1)
            if y < 1/x:
                self.c += 1
        self.e = pow(2, self.n / self.c)
        print(self.e)
        return self.c

    def get(self):
        return self.e

if __name__ == '__main__':
    # init
    context = ray.init()
    print(context.dashboard_url)
    time1 = time.time()
    increments = []
    n = 0
    c = 0
    e = 0.0


    # create actors
    for i in range(1):
        # create actor
        actor = monto.remote()

        # Submit calls to the actor. These calls run asynchronously but in  
        # submission order on the remote actor process.
        incre = actor.simulate.remote(10000000)
        n = 10000000
        increments.append(incre)

    # Retrieve final actor state.
    results = ray.get(increments)

    c = sum(results)

    # calculate e
    e = pow(2, n / c)
    # Retrieve and print the result.
    print(e)
    print("total time is: ",time.time()-time1)
```

## 计算类性能指标
经过调查，计算类的性能指标大致有以下几种：
* 资源使用率（如内存占用，CPU占用率等）：
* 效率：效率表示系统在利用分布式计算资源方面的效率。它是加速比与节点数之比。高效率意味着系统能够更有效地利用分布式资源，执行任务的效率更高。
* 平均计算时间 / 总共用时：任务完成时间
* 吞吐率（单位时间处理的任务数）
* ~~计算集群节点个数（由于Ray Launcher会自动对节点进行调整，故该指标也是较为重要的性能指标）~~
* ~~加速比：分布式/单机~~
* ~~周转时间：调度时间~~
* ~~响应时间：指从任务提交到任务第一次产生响应的时间，每个任务提交到开始运行的响应时间平均值~~
* ~~任务提交延迟（任务提交的延迟）~~

经过讨论，我们选择了如下几个指标，原因如下：
* 内存占用率、CPU占用率：反映程序对资源的利用程度，如果内存或CPU占用率过低，说明系统资源没有充分利用，可能存在性能瓶颈。例如，如果CPU占用率过低，这可能意味着程序中存在串行操作或等待磁盘I/O等问题，导致CPU无法充分利用。通过监控这些指标，我们可以确定系统在哪些资源上存在瓶颈，从而进行优化。
* 任务用时：任务提交到作业完成为止的时间，它表示从任务提交到任务完成所经过的时间。较短的任务用时意味着系统能够快速响应任务，并高效地处理任务。这对于实时系统或需要快速处理大量任务的系统特别重要。通过监控任务用时，我们可以评估计算系统的性能，并确定是否需要进行性能优化。
* 吞吐率：单位时间处理的任务数，它可以告诉我们在单位时间内系统能够处理多少任务。高吞吐率通常表示系统能够高效地处理大量任务，而低吞吐率可能表示系统存在瓶颈或资源利用不足。

## 单机版部署流程
1. 安装 Ray
```bash
pip install -U ray
pip install -U ray[default]
```

2. 启动 Ray 头节点
```bash
ray start  --head  --dashboard-host=0.0.0.0 --dashboard-port=8888 --include-dashboard=true
```
然后即可在 ```localhost:8888``` 查看 ```Ray Dashboard```

3. 启动 Ray 工作节点加入集群
```bash
ray start  --address='172.17.0.2:6379'
```
（172.17.0.2是头节点所用的 IP 地址）

3. 开始计算
```bash
python e.py
```

## 单机版优化分析

## 单机版优化结果

## 分布式部署流程
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

### （在docker中）启动 Ray
1. 启动头节点
```bash
(docker) ray start  --head  --dashboard-host=0.0.0.0 --dashboard-port=8888
```
此时可于宿主机浏览器中访问 `localhost:8888` 查看 ```Ray Dashboard```

2. 启动工作节点（可以在宿主机，也可以在同一局域网任意设备/设备之上 Docker 容器内）并连接至集群
```bash
(docker) ray start --address='172.17.0.2:6379'
```
（172.17.0.2是头节点所用的 IP 地址）

4. 通过 Docker Desktop 将脚本文件复制进容器中，推荐放置在 `/home/ray` 目录下，这是进入容器后的默认位置。

3. 开始计算
```bash
(docker) RAY_DEDUP_LOGS=0 python e.py
```

## 分布式性能测试
