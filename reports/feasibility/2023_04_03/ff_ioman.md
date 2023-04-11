### ff_ioman:

#### `ff_ioman.h`

依赖于`ff_head.h `(其实就是所有库的整合)中的`ff_ioman.h`，以下是其中比较重要的结构体定义：

```c
    typedef struct{
        uint32_t ulSector;      /* The LBA（一种定址模式） of the Cached sector. */
        uint32_t ulLRU;         /* For the Least Recently Used algorithm. */
        uint8_t * pucBuffer;    /* Pointer to the cache block. */
        uint32_t ucMode : 8,    /* Read or Write mode. */
                 bModified : 1, /* If the sector was modified since read. */
                 bValid : 1;    /* Initially FALSE. */
        uint16_t usNumHandles;  /* Number of objects using this buffer. */
        uint16_t usPersistance; /* For the persistance algorithm. */
    } FF_Buffer_t;`
        
   typedef struct _FF_IOMAN
    {
        FF_BlockDevice_t xBlkDevice; /* Pointer to a Block device description. */
        FF_Partition_t xPartition;   /* A partition description. */
        FF_Buffer_t * pxBuffers;     /* Pointer to an array of buffer descriptors. */
        void * pvSemaphore;          /* Pointer to a Semaphore object（信号量）. (For buffer description modifications only!). */
        #if ( ffconfigPROTECT_FF_FOPEN_WITH_SEMAPHORE == 1 )
            void * pvSemaphoreOpen;  /* A semaphore to protect FF_Open() against race conditions. */
        #endif
        void * FirstFile;            /* Pointer to the first File object. */
        void * xEventGroup;          /* An event group, used for locking FAT, DIR and Buffers. Replaces ucLocks. */
        uint8_t * pucCacheMem;       /* Pointer to a block of memory for the cache. */
        uint16_t usSectorSize;       /* The sector（扇区） size that IOMAN is configured to. */
        uint16_t usCacheSize;        /* Size of the cache in number of Sectors. */
        uint8_t ucPreventFlush;      /* Flushing to disk only allowed when 0. */
        uint8_t ucFlags;             /* Bit-Mask: identifying allocated pointers and other flags */
        #if ( ffconfigHASH_CACHE != 0 )
            FF_HashTable_t xHashCache[ ffconfigHASH_CACHE_DEPTH ];
        #endif
        void * pvFATLockHandle;
    } FF_IOManager_t;
```

#### `ff_ioman.c`函数总结

`FF_IOManager_t * FF_CreateIOManager( FF_CreationParameters_t * pxParameters, FF_Error_t * pError )`: 初始化一个FF_IOMAN对象，获取扇区大小、cache大小等对象信息

`FF_Error_t FF_DeleteIOManager( FF_IOManager_t * pxIOManager )`：删除一个FF_IOMAN对象，释放其占用的所有空间

`void FF_IOMAN_InitBufferDescriptors( FF_IOManager_t * pxIOManager )`：补充FF_IOMAN中的内容buffer descriptor，DMA 模块收发数据的单元被称为 BD（Buffer Description，缓存描述符），每个包都会被分成若干个帧，而每个帧则被保存在一个 BD 中。相当于一个buffer的指针。

`FF_Error_t FF_FlushCache( FF_IOManager_t * pxIOManager )`：清空所有无活跃句柄的cache

`FF_Buffer_t * FF_GetBuffer( FF_IOManager_t * pxIOManager, uint32_t ulSector, uint8_t ucMode )`:获取一个符合要求的buffer

`FF_Error_t FF_ReleaseBuffer( FF_IOManager_t * pxIOManager,FF_Buffer_t * pxBuffer )`:释放

`int32_t FF_BlockRead( FF_IOManager_t * pxIOManager,uint32_t ulSectorLBA,uint32_t ulNumSectors,void * pxBuffer, BaseType_t xSemLocked )`: 读一个指定位置的块，其中块是cache的一部分（基础知识）

`int32_t FF_BlockWrite( FF_IOManager_t * pxIOManager,uint32_t ulSectorLBA,uint32_t ulNumSectors,void * pxBuffer,BaseType_t xSemLocked )`:写， 同上

`static FF_Error_t prvDetermineFatType( FF_IOManager_t * pxIOManager )`: 根据Microsoft的文档，实际型号为：FAT-12、FAT-16和FAT-32可以通过查看数据集群的总数来找到分区。但不一定完全准确，进一步根据FAT table中的前12/16个bits可以决定实际文件系统类型

`static BaseType_t prvIsValidMedia( uint8_t media )`:确认MBR(主引导扇区)中的media byte是否有效

`FF_Error_t FF_PartitionSearch( FF_IOManager_t * pxIOManager,FF_SPartFound_t * pPartsFound )`：在磁盘中搜索所有主分区和扩展/逻辑分区

`FF_Error_t FF_Mount( FF_Disk_t * pxDisk,BaseType_t xPartitionNumber )`:装载指定的分区，即由提供的FF_IOManager_t对象指定的卷

`int32_t FF_GetPartitionBlockSize( FF_IOManager_t * pxIOManager )`: The purpose of this function is to provide API access to information that might be useful in special cases. Like USB sticks that require a sector knocking sequence for security. After the sector knock, some secure USB sticks then present a different BlockSize.

`uint64_t FF_GetVolumeSize( FF_IOManager_t * pxIOManager )`:返回挂载（类似于文件结构）的分区的大小

### ff_format

`static FF_Error_t prvFormatGetClusterSize( struct xFormatSet * pxSet,BaseType_t xPreferFAT16,BaseType_t xSmallClusters )`:pxSet->ucFATType == FF_T_FAT16决定应使用FAT32还是FAT16，并尝试找到最佳集群大小

`static void prvFormatOptimiseFATLocation( struct xFormatSet * pxSet )`:优化文件系统的储存的位置

`static FF_Error_t prvFormatWriteBPB( struct xFormatSet * pxSet,const char * pcVolumeName )`: 写入[BIOS 参数块 - 维基百科 (wikipedia.org)](https://en.wikipedia.org/wiki/BIOS_parameter_block)，这个描述的是硬盘分区

`static FF_Error_t prvFormatInitialiseFAT( struct xFormatSet * pxSet,int32_t lFatBeginLBA )`:初始化并清理FAT(File Allocation Table)

`static FF_Error_t prvFormatInitialiseRootDir( struct xFormatSet * pxSet,int32_t lDirectoryBegin,const char * pcVolumeName)`: 初始化或者清空根目录

`static FF_Error_t prvPartitionPrimary( struct xPartitionSet * pxSet )`：创建初始或扩展分区

### ff_sys

将一系列文件系统同意抽象成一个数组，进行初始化、增加、删除和寻找文件等操作（通过pcPATH文件路径）