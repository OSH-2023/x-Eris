# ErisFS 结题报告
## 项目简介 [wsr]
## 项目背景（极简）[wsr]
## 项目架构[wsr]
## 开发过程
### 第一阶段
#### efs.c[wsr]
#### efs_file.c[hty]
#### efs_fs.c[lyb]
efs_fs的作用是对文件系统进行管理，功能包括文件系统的挂载卸载、查找路径上的文件系统、查找设备上的文件系统、对文件系统状态进行控制，以下先介绍相关结构体的功能：
- `struct efs_filesystem_ops`：文件系统操作表，保存文件系统名及其操作函数，包括文件系统名、文件系统对文件操作的函数表`const struct efs_file_ops *fops`以及文件系统操作函数，如mount、unmount等
- `struct efs_filesystem`：已挂载的文件系统表 保存文件系统与设备、路径等信息
- `struct efs_partition`：文件系统分区表 文件系统分配空间信息包括文件系统类型、分区大小等
- `struct efs_mount_tbl`：文件系统挂载表 对设备、路径、文件系统的总管理，包括设备名、路径、文件系统类型等

通过上述结构体，文件系统的各项操作（一般由文件系统自身实现）、文件系统使用的硬件空间、设备、路径等信息都完备地实现了记录。实现挂载等功能时只需对相关更底层的函数调用或是对信息进行处理。efs_fs.c中的函数实质上是对各种结构体的完善或控制。
- `efs_register`：注册文件系统，保存文件系统名及其操作函数到`filesystem_operation_table`
- `efs_mount`：挂载文件系统，将文件系统与设备、路径相联系
- `efs_unmount`：卸载文件系统，清空文件系统操作表、路径、关闭设备
- `efs_mkfs`：格式化文件系统，需要调用文件系统的mkfs函数
- `efs_statfs`：获取文件系统信息，需要调用文件系统的statfs函数
- `efs_filesystem_lookup`：查找路径上的文件系统
- `efs_filesystem_get_mounted_path`：查找设备上挂载的文件系统等
- `efs_filesystem_get_partition`：获取分区表

#### efs_posix.c[wcx]
#### ramfs[lrs]
### 第二阶段
#### Posix 补充[wcx]
#### device.c[lyb]
本项目设计中ErisFS不止局限于对单一设备的控制，而是能够对多个设备，如SD卡、Flash等进行统一的控制管理，但由于硬件限制，并未测试device管理对设备的实际效果，以下对device管理做简要介绍：
`struct efs_device`：保存设备状态及相关操作函数，包括设备开关信息、设备ID、设备接口，如init、open、close等
`efs_device_open/close`：开关设备检查设备信息，并开关设备
`efs_device_read/write`：读写设备 检查设备信息，并读写设备
`efs_device_find`：查找设备 查找已实现的设备，并返回其结构体

值得提出的是，device管理的核心是将底层的设备操作函数与上层抽象层链接以方便管理，理想状态下能够同时实现对板子上SD卡、Falsh等存储设备的统一管理。

### 第三阶段
#### FATFS 移植[wcx]
FATFS适配层主要实现了vfs虚拟层调用函数和FATFS的基本函数之间传入参数的适配，并且通过FreeRTOS中特有的空间分配释放等函数，为FATFS进行空间的分配。

其中，又分为文件系统操作函数和文件操作函数，文件系统操作函数包括efs_fatfs_mount, efs_fatfs_unmount，efs_fatfs_mkfs,efs_fatfs_statfs,efs_fatfs_unlink,efs_fatfs_stat, efs_fatfs_rename；文件操作函数包括efs_fatfs_open, efs_fatfs_close, efs_fatfs_ioctl, efs_fatfs_read, efs_fatfs_write, efs_fatfs_lseek, efs_fatfs_getdents。

大致函数内容如下所示，通过get_disk获取设备编号，然后通过调用FATFS内置的函数进行取消挂载的操作，其他函数还涉及部分文件系统挂载、文件夹创建等涉及到的空间分配的函数。

```c
int efs_fatfs_unmount(struct efs_filesystem *fs)
{
    FATFS *fat;
    FRESULT result;
    int  index;
    char logic_nbr[3] = {'0',':', 0};

    fat = (FATFS *)fs->data;

    if (fat == NULL)
    {
        // printf("[efs_fatfs.c] failed to fetch fat in efs_fatfs_unmount!\r\n");
        return -1;
    }

    /* find the device index and then umount it */
    index = get_disk(fs->dev_id);
    if (index == -1) /* not found */
    {
        // printf("[efs_fatfs.c] failed to get disk in efs_fatfs_unmount!\r\n");
        return -1;
    }

    logic_nbr[0] = '0' + index;
    result = f_mount(NULL, logic_nbr, (unsigned char)0);
    if (result != FR_OK)
        return fatfs_result_to_errno(result);

    fs->data = NULL;
    disk[index] = NULL;
    vPortFree(fat);

    return 0;
}
```
#### 硬件移植[lrs]
### 第四阶段
#### 经典加密[hty]
#### AES加密[hty]
## 项目总结
### 对比中期汇报[wsr]
### 项目意义[wsr]
### 分工致谢
