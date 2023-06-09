# 嵌入式设备的文件系统
> 本篇报告主要介绍了FreeRTOS-Plus-FAT以及RT-Thread中的文件系统实现细节。
## 早期嵌入式设备的文件系统
在早期的嵌入式系统中，需要存储的数据比较少，数据类型也比较单一，往往使用直接在存储设备中的指定地址写入数据的方法来存储数据。然而随着嵌入式设备功能的发展，需要存储的数据越来越多，也越来越复杂，这时仍使用旧方法来存储并管理数据就变得非常繁琐困难。因此我们需要新的数据管理方式来简化存储数据的组织形式，需要新的文件系统。

## FreeRTOS (约 6w lines) 的文件系统 
没有提供文件系统，如果想要读写文件，有以下两种途径：
* 先实现单个文件系统的接口，并将其注册到标准C库中。挂载之后通过标准C库的文件读写函数来操作文件。
* 编写 VFS，支持多个文件系统的挂载，提供统一的接口读写文件。

## FreeRTOS-Plus-FAT (约 1w lines)
FreeRTOS-Plus-FAT 是一种开源、线程感知和可扩展的 FAT12/FAT16/FAT32 DOS/Windows 兼容 嵌入式 FAT 文件系统（VFS），与 RTOS 一同或分别使用。它提供了一个API来访问文件系统，并支持多种存储介质。

### 源代码组织

- 主要
  * ```ff_dir```: 用于访问文件夹中内容
  * ```ff_fat```: 用于访问 FAT 文件系统
  * ```ff_file```: 用于文件读写
  * ```ff_ioman```: 管理缓存和挂载读写对象（介质）
  * ```ff_format```: 格式化或分区介质
  * ```ff_locking```: 加锁？
  * ```ff_memory```: 从内存读取数据
  * ```ff_stdio```: 用于文件管理（统计），相对路径转换
  * ```ff_sys```: 用于映射文件系统到根目录
- 辅助
  * ```ff_headers```: 管理所有头文件
  * ```ff_time```: 获取时间
  * ```ff_error```: 用于错误处理
  * ```ff_crc```: 用于计算 CRC（循环检验码）
  * ```ff_string```: 字符串库
- 驱动
  * 各处理器相应的文件系统驱动

### 采用标准 eerno 值
FreeRTOS-Plus-FAT 文件系统的标准 API 与标准 C 库使用相同的 errno 值。

标准 C 库中的文件相关函数返回 0 表示通过，返回 -1 则表示失败。如果返回 -1，则失败的原因 存储在名为 errno 的变量中，须单独检查。 同样，FreeRTOS-Plus-FAT 的标准 API 返回 0 表示通过，返回 -1 则表示失败， 该 API 还会针对各项 RTOS 任务维护 errno 变量。

### API 设计
包括两部分，标准函数与磁盘管理函数。
* 标准函数
  * 目标/文件夹写入函数
    * ```ff_mkdir("/wy")``` 创建文件夹
  * 读取&写入函数
    * ```ff_fopen( pcFileName, "w" )```打开文件流
    *  ```ff_fwrite( pcRAMBuffer, fsRAM_BUFFER_SIZE, 1, pxFile )```写入文件流
  * 实用程序函数
    * ```ff_remove() ```移除文件
    * 查找、统计、重命名文件
* 磁盘管理函数
  * ```FF_Partition()``` 对媒体分区
  * ```FF_Format()``` 对分区格式化
  * ```FF_Mount()``` 挂载分区
  * ```FF_FS_Add()``` 添加挂载分区到 FreeRTOS-Plus-FAT 虚拟文件系统， 它将显示为文件系统根目录下的目录。

> 媒体是用于存储文件的物理设备。适用于 嵌入式文件系统的媒体的示例包括 SD 卡、固态磁盘、NOR 闪存芯片、NAND 闪存芯片和 RAM 芯片。 媒体不能用于保存 FreeRTOS-Plus-FAT 文件系统，直至它被分区。 将媒体划分为多个单元，每个单元被称为一个分区。然后，可以对每个分区进行格式化以保存其文件系统。
> 
> FF_Format() 将动态确定要使用的 FAT 类型和簇大小。 簇大小将与簇计数相关，而簇 计算和FAT 类型相关。 xPreferFAT16 和 xSmallClusters 参数 允许指定首选项。 例如，对于小 RAM 磁盘 将两个参数都设置为 true 以使用 FAT16 与小簇，对于 大 SD 卡，则将两个参数都设置为 false 以使用 FAT32 和 大簇。 较大的簇可以更快被访问，而较小的簇 浪费更少的空间，因为它们在文件末尾会有较少的 未使用块。

### 使用方式示例 
* ```FF_SDDiskInit("/")``` 挂载/初始化
* ```ff_mkdir("/wy")``` 创建文件夹
* ```ff_fopen( pcFileName, "w" )```打开文件流
* ```ff_fwrite( pcRAMBuffer, fsRAM_BUFFER_SIZE, 1, pxFile )```写入文件流

## RT-Thread 文件系统 DFS
此文件系统有较多简介，可供设计参考。
### 特点
* 为应用程序提供统一的 POSIX 文件和目录操作接口：read、write、poll/select 等。

* 支持多种类型的文件系统，如 FatFS、RomFS、DevFS 等，并提供普通文件、设备文件、网络文件描述符的管理。

* 支持多种类型的存储设备，如 SD Card、SPI Flash、Nand Flash 等。

### POSIX 文件系统接口
POSIX 表示可移植操作系统接口（Portable Operating System Interface of UNIX，缩写 POSIX），POSIX 标准定义了操作系统应该为应用程序提供的接口标准，是 IEEE 为要在各种 UNIX 操作系统上运行的软件而定义的一系列 API 标准的总称。

POSIX 标准意在期望获得源代码级别的软件可移植性。换句话说，为一个 POSIX 兼容的操作系统编写的程序，应该可以在任何其它 POSIX 操作系统（即使是来自另一个厂商）上编译执行。RT-Thread 支持 POSIX 标准接口，因此可以很方便的将 Linux/Unix 的程序移植到 RT-Thread 操作系统上。

在类 Unix 系统中，普通文件、设备文件、网络文件描述符是同一种文件描述符。而在 RT-Thread 操作系统中，使用 DFS 来实现这种统一性。有了这种文件描述符的统一性，我们就可以使用 poll/select 接口来对这几种描述符进行统一轮询，为实现程序功能带来方便。

使用 poll/select 接口可以阻塞地同时探测一组支持非阻塞的 I/O 设备是否有事件发生（如可读，可写，有高优先级的错误输出，出现错误等等），直至某一个设备触发了事件或者超过了指定的等待时间。这种机制可以帮助调用者寻找当前就绪的设备，降低编程的复杂度。

> **总结**： 通过支持 POSIX 文件系统接口，可以很方便的支持 Linux/Unix 的程序；通过使用同一种文件描述符，可以统一操作，降低复杂度。

### 虚拟文件系统层
用户可以将具体的文件系统注册到 DFS 中，如 FatFS、RomFS、DevFS 等。
* FatFS 是专为小型嵌入式设备开发的一个兼容微软 FAT 格式的文件系统，采用 ANSI C 编写，具有良好的硬件无关性以及可移植性，是 RT-Thread 中最常用的文件系统类型。

* 传统型的 RomFS 文件系统是一种简单的、紧凑的、只读的文件系统，不支持动态擦写保存，按顺序存放数据，因而支持应用程序以 XIP(execute In Place，片内运行) 方式运行，在系统运行时, 节省 RAM 空间。

* Jffs2 文件系统是一种日志闪存文件系统。主要用于 NOR 型闪存，基于 MTD 驱动层，特点是：可读写的、支持数据压缩的、基于哈希表的日志型文件系统，并提供了崩溃 / 掉电安全保护，提供写平衡支持等。

* DevFS 即设备文件系统，在 RT-Thread 操作系统中开启该功能后，可以将系统中的设备在 /dev 文件夹下虚拟成文件，使得设备可以按照文件的操作方式使用 read、write 等接口进行操作。

* NFS 网络文件系统（Network File System）是一项在不同机器、不同操作系统之间通过网络共享文件的技术。在操作系统的开发调试阶段，可以利用该技术在主机上建立基于 NFS 的根文件系统，挂载到嵌入式设备上，可以很方便地修改根文件系统的内容。

* UFFS 是 Ultra-low-cost Flash File System（超低功耗的闪存文件系统）的简称。它是国人开发的、专为嵌入式设备等小内存环境中使用 Nand Flash 的开源文件系统。与嵌入式中常使用的 Yaffs 文件系统相比具有资源占用少、启动速度快、免费等优势。
  
> **总结**：可考虑选择一或两种不太复杂的文件系统为 FreeRTOS 添加支持，如 RomFS。 不要涉及网络文件系统。

### 设备抽象层
设备抽象层将物理设备如 SD Card、SPI Flash、Nand Flash，抽象成符合文件系统能够访问的设备，例如 FAT 文件系统要求存储设备必须是块设备类型。

不同文件系统类型是独立于存储设备驱动而实现的，因此把底层存储设备的驱动接口和文件系统对接起来之后，才可以正确地使用文件系统功能。

## 与本选题方向相关的总结
设计 VFS 时，可以参考 RT-Thread 的三层结构组织形式、FreeRTOS-Plus-FAT 的API设计理念，在 FreeRTOS-Plus-FAT 继续拓展优化。

例如，应继续采用标准 eerno 值以保持兼容性。同时，可以通过保持 POSIX 文件系统接口，并且添加 FreeRTOS-Plus-POSIX 来方便的运行从 Linux/Unix上移植的程序。
> 注：FreeRTOS-Plus-POSIX 仅仅实现了部分 POSIX 接口，无法仅使用此包装器将现有的 POSIX 兼容应用程序或 POSIX 兼容库移植到 FreeRTOS 内核上运行。
