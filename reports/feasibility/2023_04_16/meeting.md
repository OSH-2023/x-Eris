# 2023_04_16 会议记录

## 摘要
- 理论依据
  * FreeRTOS信号量相关 【wcx】
  * （FreeRTOS提供的相关函数）
  * RT-Thread的文件系统抽象设计 【wsr】
  * RT-Thread的文件系统相关流程分析（挂载、...）【lyb】
  * （缓存）
  * 各个文件系统的格式区别 【hty】
- 技术依据
  * 使用QEMU搭建FreeRTOS系统的可行性 【lrs】
  * 使用QEMU进行文件系统开发的可行性【lrs】
    + FreeRTOS-PLUS-FAT的过时性
  * （FreeRTOS + QEMU 监测到已挂载设备的demo）
  * 各个文件系统的库支持（Ramfs -> 直接memcpy、FAT -> 已经有FATFS库支持、jffs2 -> ?）【hty】
- 创新点
  * FreeRTOS上的VFS 【wsr】
  * 信号量 - 安全性 【wcx】
  * 缓存 - 性能 【lyb】
  * POSIX接口 【wsr】
- 概要设计
  * 需求目标

  * 总体结构功能，处理流程，外部接口，模块设计

  * 开发路线
  
## Bonus
理解了不同文件系统底层函数如何实现，确保了项目的可行性。

## 计划
本周三前完成各部分编写，周三下午开会讨论最后部分。

