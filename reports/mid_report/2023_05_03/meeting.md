# 2023_05_03 会议记录

## 摘要
* 调研报告part1
  - 项目概述 【1p】
  - 背景介绍 
    + 嵌入式操作系统 - FreeRTOS 【1-2p】
    + 文件系统 - FATFS/JFFS2 【1p】
  - 前瞻性、重要性
    + “随着技术发展，嵌入式设备的存储空间不断增加，直接读写内存地址的方式不再可行，对规范文件系统的需求在逐渐上升” -> 【1p】
    + FreeRTOS 现有的虚拟文件系统兼容性过低 【1-2p】
    + 安全性保护缺失 / 性能表现不佳 【1p】
“然后我们进行了可行性的调研....->”
* 可行性报告part2
  - 创新点
    + 总共四点 -> 【2p】
    + 与前面前瞻性重要性可以呼应
  - 理论依据
    + RT-Thread架构可以参考的部分 【1-2p】
    + 缓存相关 【1p】
  - 技术依据
    + FreeRTOS 信号量 【1p】
    + QEMU模拟器运行FreeRTOS、QEMU挂载磁盘相关实际操作介绍 
  - 开发路线
    + 总体结构 【1p】
    + 开发路线 ->内容全放进

## 计划
分工制作ppt和脚本，发送到群里进行整合，下周一进行进一步讨论。