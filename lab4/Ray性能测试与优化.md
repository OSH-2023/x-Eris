# Ray性能测试与优化
## 性能指标
- 周转时间：任务提交到作业完成为止的时间，最根本的反映程序运行速度的指标。
- 资源使用率：反映程序对资源的利用程度
    - CPU使用率
    - 内存占用率
- 吞吐率：单位时间处理的任务数

**选择依据：** 上述指标从两个最基本的方面来体现Ray的性能，即处理速度与使用资源。一般而言，我们希望程序运行的速度更快、使用资源更少，但是另一方面，在资源空闲较大时，我们也能够通过增加并行性而使用更多的资源以获得更高的运行速度。

## 测试程序
采用蒙特卡洛方法估计$e$的值，
> 如下图所示，用蒙特卡洛方法随机在范围为$1\le x \le2, 0 \le y \le 1$的矩形方格中撒n个点，统计$y=\frac{1}{x}$内点的个数，记为c
由定积分可算出这部分面积为ln2，即$e^{\frac{c}{n}} = 2$，即可求出$$e=2^{\frac{c}{n}}$$
![](\img\lnx.png)

#### 原程序：
直接模拟10000000次撒点实验，计算$e$的估计值，核心代码如下：
```python
        self.n += times
        for i in range(times):
            x = random.uniform(1, 2)
            y = random.uniform(0, 1)
            if y < 1/x:
                self.c += 1
        self.e = pow(2, self.n / self.c)
        print(self.e)
        return self.c
```

```python
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
```

#### 优化程序：
增加程序并行性能，将原有的10000000次撒点分为8个任务执行，核心代码如下：
```python
for i in range(8):
        # create actor
        actor = monto.remote()

        # Submit calls to the actor. These calls run asynchronously but in  
        # submission order on the remote actor process.
        incre = actor.simulate.remote(1250000)
        n += 1250000
        increments.append(incre)

    # Retrieve final actor state.
    results = ray.get(increments)

    c = sum(results)

    # calculate e
    e = pow(2, n / c)
```

## 单机性能测试及优化
|           | 周转时间  |CPU占用率  | 内存占用率    |吞吐量(Tasks)|
|:---       | :---:     |:----:     |:---:          |:---:|
| 原程序    | 4.57s|13%   |40.9%|2|
| 优化程序  | 2.07s| 16.1%  |42.1%|16|

由此可见，使用优化程序后Ray并行性提升、对空闲资源的使用更高、运行更快。
除此之外，我们还进行了更改num_cpus数量的简要测试（以下数据均以原程序为测试对象）
|num_cpus|周转时间|
|:---:|:---:|
|1|4.56s|
|2|4.48s|
|4|4.48s|
|8|4.43s|
可以看到，对于本测试程序，CPU核心数量并不显著影响运行时间