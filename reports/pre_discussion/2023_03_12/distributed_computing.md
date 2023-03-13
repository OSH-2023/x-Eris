# 分布式计算 简要调研
## 现有框架
### Rain
#### 简介：
[Rain Overview](https://substantic.github.io/rain/docs/overview.html)
* 主要基于 ```Rust```，上一次更新于 2018 年。
* Task: **functions or ex programs** that reads inputs and produces outputs.
* Data objects: **immutable obejects** that are read and created by tasks.
  * ```blob```: Binary data block.
  * ```dir```: Directory structure.

#### 用法：

需要手动建立进程（sessions），提交任务（submit），等待计算完成（wait_all）；
除了内置任务外，也可以调用外部代码，或使用装饰器 ```@remote``` 直接运行     ```python``` 代码。

任务间数据调用可能需要手动设置延迟。

#### 缺点 / 可能的改进方向：
* 需要手动调控进程，不够自动化
* 可调控的参数不多，目前仅有 CPU 数目 -> GPU、 TPU、 硬盘空间
* 更好的调度程序 （目前的主要基于启发式以及预定规则）
* 更强的鲁棒性，以避免崩溃，或者在崩溃后自动恢复
* 流对象支持，改进当前需要等待全部输出才能进行下一个阶段的机制。


### Ray
#### 简介：
[Ray v2 Architecture](https://docs.google.com/document/d/1tBw9A4j62ruI5omIJbMxly-la5w4q_TjyJgJL_jN2fI/preview)
* Ray Core （帮助构建可分布计算的python文档）
  * Tasks: **functions** that can be executed asynchronous and remotely. （无状态的，仅与参数有关）
    * Task 的调用会被**并行**执行
    * 注册任务（```@ray.remote``` 装饰器）
    * 提交任务（```fn.remote()``` 调用）
    * 获得一个结果的 ```ObejctRef``` 对象（非阻塞） 
    * 按需阻塞获得结果（```ray.get()```获取）
  * Actors: **classes**, can be instantiated as workers. （有状态的）
    * Actors 的方法调用会被**串行**执行。
    * 注册 Actor（```@ray.remote``` 装饰器）
    * 实例化 Actor（```class.remote``` 实例化为 Worker）
    * 提交方法调用（```fn.remote()``` 调用）
    * 获得一个结果的 ```ObejctRef``` 对象（非阻塞） 
    * 按需阻塞获得结果（```ray.get()``` 获取）
  * Objects: remote **objects(data)** that can be stored anywhere in the cluster. Accessed by reference.

* Ray AIR（基于Core的库，帮助构建AI相关工作）

#### 架构 (v1)：
主要分为：App Layer 与 System Layer
##### 应用层
有三种进程：Driver（执行用户程序）、Worker（执行无状态任务/函数）、Actor（执行有状态任务）
##### 系统层
* Global Control Store
  * 维护全局状态：Object Table、Task Table、Function Table、Event Log
  * 记录对象、任务存在于哪一个节点、定义的远程函数以及任务日志
* Distributed Scheduler
  * 主要有两层：全局调度器和本地节点的调度器
  * 若任务在本节点内被满足需求，则任务在节点就被调度，否则传递至全局调度（依据输入和等待时间选择节点）
* Distributed Object Store
  * 每个节点上实现一个对象存储器，远程输入以及输出总会先写到节点存储器，减少了瓶颈

#### 架构 (v2)
##### 应用层
节点仅有两种进程：Driver（执行用户程序）、Worker（执行任务，包括无状态Task或者是Actor的方法调用）

##### 系统层
每个 Worker 存储 ownership table（Objects 的应用） 及 in-progress store(存储小 Objects)

每个节点还拥有 Raylet，包含 scheduler（v1中的节点调度器）, shared-memory object store（v1中的节点对象存储器）

节点中有一个特殊的 head node，它拥有：
* Global Control Service，调度节点任务，存储各种信息。有 fault tolerance，使得GCS可以运行在任意节点上（避免单头节点失效引起分布式系统奔溃）
* Driver 进程，执行最高级别的应用程序，可提交任务
* 其他的节点功能

##### Ownership
利用 ObjectRef 创建对对象的引用。
* 优点：低延迟，高并发，简单可靠

#### Memory
* **Heap memory** used by Ray workers during task or actor execution, small Ray objects, Ray metadata.

* **Shared memory** used by large Ray objects (ObjectRef).
## Dask
## Spark