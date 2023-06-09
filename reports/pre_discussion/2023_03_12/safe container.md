#容器优化
####虚拟化
虚拟化或虚拟技术（Virtualization）是一种资源管理技术，是将计算机的各种实体资源（CPU、内存、磁盘空间、网络适配器等），予以抽象、转换后呈现出来并可供分割、组合为一个或多个电脑配置环境。本质是指资源的抽象化,提高资源的利用率。

####容器
容器是一个标准化的软件单元，它将代码及其所有依赖关系打包，以便应用程序从一个计算环境可靠快速地运行到另一个计算环境。

| 不同点    |           container    |                    VM |
| :------: | :-----------------------: | :---------------: |
| 启动速度 |      秒级                      |    分钟级 |
| 运行性能  | 接近原生（直接在内核中运行） |  5%左右损失 |
| 磁盘占用  |     MB     |  GB |
| 隔离性    | 进程级别        | 系统级别 |
| 操作系统  | 主要支持Linux       | 几乎所有 |
| 封装程度  | 打包项目代码和依赖关系，共享宿主内核|完整的操作系统，与宿主机隔离|

####容器隔离缺陷
容器隔离主要基于内核提供的namespace、cgroup、seccomp等机制，实现容器内的资源、文件、系统调用等限制和隔离。由于其仍然采用共内核的机制，尤其在公有云场景下，具有较大的攻击面。

####优化思路
#####减小攻击面
由于攻击主要因共用内核，所以可以劫持容器的系统调用指令，并模拟操作系统分析处理指令。
#####结合虚拟化
考虑到虚拟化的安全性和速度，对虚拟化进行阉割，保留运行容器和其中程序的必要功能，减轻常规虚拟化开销，实现结合容器化和虚拟化。
