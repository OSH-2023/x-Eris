# 2023_06_03 会议记录
## Lab4 部分
进行了相关测试运行，实验整体进行留待下次会议讨论。

## EFS 部分
通过一晚上的调试，目前修改完成了Makefile，可以正常编译。但仍有不少 warnings 未解决，需要各组员修改自己负责部分的代码，如有必要也可以对其他部分进行修改。

### 如何将 ErisFS 加入 Demo
0. 在进行这一部分之前，强烈建议您先阅读 FreeRTOS x QEMU 的有关文档并且尝试运行跑通 Demo (main_blinky)。
1. 将 ```ErisFS``` 放至 ```Demo/CORTEX_MPS2_QEMU_IAR_GCC``` 下
2. 用 ```ErisFS/replace``` 里的 ```main_blinky.c``` 和 ```Makefile``` 文件替换掉 ```Demo/CORTEX_MPS2_QEMU_IAR_GCC/main_blinky.c``` 和 ```Demo/CORTEX_MPS2_QEMU_IAR_GCC/build/gcc/Makefile```
3. 运行 ```cd /build/gcc && make``` 即可编译
4. 如果需要仅查看自己负责文件的有关错误信息，可以在 ```make``` 的输出内容中挑选特定相关编译指令单独编译。

## 计划
本周三进行线下会议，主要内容为 Lab4 的实现，附带 EFS 的融合调试。