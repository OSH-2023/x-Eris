# 理论依据【可拓展性考察】
## FreeRTOS-Plus-FAT的具体实现分析
### API 调用相关
FreeRTOS-Plus-FAT 为用户提供API的主要是 ```ff_stdio.h```，里面的函数多与常用stdio函数相近。例如，我们可以通过查看用户调用```ff_stdio```中的```ff_mkdir()```函数，来了解FreeRTOS-Plus-FAT的实现。

```
ff_mkdir() in ff_stdio
│   
├── FF_FS_Find() in ff_sys
│   └─── FF_Mounted() in ff_ioman
│    
└── FF_MkDir() in ff_dir
    |── FF_FindEntryInDir(), FF_FindDir()
    └── FF_CreateClusterChain() in ff_fat

```
可以看到通过上层的API函数，最终会调用到底层的```ff_fat/FF_CreateClusterChain()```函数，只有这个函数与FATFS关系紧密，作用是创建一个新的簇链，用于存放新的文件。

### 文件系统存储相关
FreeRTOS-Plus-FAT中有关文件系统信息主要存储在以下几个结构体中，例如：
* FF_DirEnt_t
  - 文件夹相关信息
* FF_DirHandler_t
  - 映射文件夹到设备驱动
* FF_Disk_t
  - 媒体驱动相关信息
* FF_Partition_t
  - 硬盘分区相关信息

对于我们的项目目标，可以尝试将FreeRTOS-Plus-FAT中的有关于特定文件系统的函数调用更改为通过查表调用对应文件系统的方式，从而实现对多种文件系统的支持。

但也可能出现一些问题，因为FreeRTOS-Plus-FAT中的某些函数实现是与FATFS紧密相关的，如果希望兼容其他的文件系统可能需要作出较多改变。同时FreeRTOS-Plus—FAT的代码组织比较复杂，因此另一条可供备选的道路就是参照RT-Thread的架构从零开始构建一个新的VFS。

## RT-Thread架构分析
### 代码组织
* dfs.c, dfs_fs.c, dfs_posix.c, dfs_file.c
  - 文件系统相关的通用操作
* filesystems/cromfs, devfs, ramfs.../dfs_x.c
  - 具体文件系统的操作实现

RT-Thread的架构设计以及文档较为完善。它首先提供了```dfs_posix.c```为用户提供符合POSIX标准的文件系统API，例如```open()```、```read()```等。通过这个文件，调用了```dfs_file```, ```dfs_private```的稍底层的函数。这些函数最终会调用到各个文件系统具体的函数。
我们可以通过查看用户调用```dfs_posix.c```中的```mkdir()```函数，来了解RT-Thread的实现。

```
mkdir() in dfs_posix
│   
├── fd_new(), fd_release(), fd_get() in dfs.c
│    
└── dfs_file_open() in dfs_file
    └── fnode->ops->open() (dfs_x_open() in filesystems/x/dfs_x.c)
        
```
可以看到 POSIX 标准 API的下一层调用主要分为两部分，一部分是通用的文件系统操作，例如对文件标识符的操作；另一部分是涉及具体文件系统的具体操作（通过不同文件节点（vnode）对应的操作链不同），比较清晰易懂。

### 文件系统存储相关
* dfs_filesystem
  - 具体文件系统相关信息
  - dfs_filesystem_ops (mount, unmount)：具体文件系统操作

* dfs_fnode
  - 文件节点相关信息（参照 Linux VFS）
  - dfs_file_ops (open, close, write)：具体文件操作

* dfs_fd
  - 文件描述符相关信息

## 小结
综上所属，本小节主要细致分析了FreeRTOS和RT-Thread的文件系统组织以及存储信息设计，可以看到RT-Thread的DFS设计更加清晰易懂，而FreeRTOS-Plus-FAT的设计则更加紧密。

在实现上，有两条路径可选：

* 直接基于FreeRTOS-Plus-FAT的设计，实现对多种文件系统的支持。
  - 但由于与FATFS关系过于紧密，可能底层函数难以更改。
  - 文件系统设计架构较为复杂，可能需要较多的时间去理解。
* 借鉴RT-Thread的设计，从零开始构建一个新的VFS。
  - RT-Thread的设计更接近Linux的VFS，文档更多也更加清晰易懂，因此容易理解实现。
  - RT-Thread的架构非常解耦，因此可以很方便地添加多种文件系统的支持、或是改进VFS部分而不造成其他影响。


> 上课建议：存储空间管理，性能优化，FPL，NAND