# 2023_03_30 会议记录
## 摘要
对如何完善调研报告进行了讨论。
## 项目相关
* 基本项目内容：以C语言编写，基于FreeRTOS-Plus-FAT进行兼容性拓展及安全性能优化。

### 基本工作
* 兼容性
  - 添加支持的文件系统（【闪存】jffs2、【磁盘 / 只读】ROMFS ）
  - 支持 POSIX 接口

### 后期优化
* 安全性
  - 备份
* 性能
  - 简单优化（预读、缓存）、利用工具评估量化分析
  - MMU支持

## 计划
> 选题报告（15页），截止日期：2023年4月5日。



周末前，将项目背景、相关工作部分的报告填入 tex 文件。

周末通过共享文档完成立项依据、前瞻性 / 重要性分析部分的报告

下周一开会，讨论可行性报告分工。
