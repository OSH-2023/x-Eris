## FreeRTOS-FAT函数分析

### ff_fread

函数调用关系：

```c
size_t ff_fread( void * pvBuffer,size_t xSize,size_t xItems,FF_FILE * pxStream )
	|--int32_t FF_Read( FF_FILE * pxFile,uint32_t ulElementSize,uint32_t ulCount,uint8_t * pucBuffer )
		|--FF_ReadPartial();FF_BlockRead();FF_ReadClusters();
			|--FF_GetBuffer,FF_ReleaseBuffer
                |--FF_PendSemaphore( pxIOManager->pvSemaphore );FF_ReleaseSemaphore( pxIOManager->pvSemaphore );
```

### FF_Read

该函数通过以下五个步骤来完成读取任务：

1. 读取字节直到达到扇区边界：FF_ReadPartial()
2. 读取扇区直到达到簇边界：FF_BlockRead()
3. 读取整个簇：FF_ReadClusters()
4. 读取剩余扇区：FF_BlockRead()
5. 读取剩余字节：FF_ReadPartial()

#### FF_ReadPartial() 

当ffconfigOPTIMISE_UNALIGNED_ACCESS为0或未定义时，它将通过调用FF_GetBuffer等函数以标准方式读取文件。如果文件缓冲区pxBuffer无法获取，则返回一个错误信息；否则将数据从缓冲区pxBuffer中复制到pucBuffer中，并返回已读取的字节数ulBytesRead，释放该缓冲区并将文件指针ulFilePointer增加ulCount。

而当ffconfigOPTIMISE_UNALIGNED_ACCESS不为0时，它将以优化的方式读取文件。在读取前，程序首先检查当前块是否需要读取。如果是，则调用FF_BlockRead函数将该块读入缓冲区中，并标记缓冲区为有效(即FF_BUFSTATE_VALID)。然后将数据从缓冲区pxFile->pucBuffer + ulRelBlockPos中复制到pucBuffer中，并返回已读取的字节数ulBytesRead。如果在此过程中发现这个块不是当前读取的最后一个块，则暂时不需要写回缓冲区。否则，如果该文件处于更新模式并且文件内容发生了更改，则调用FF_BlockWrite函数将缓冲区数据重新写入该块中。最后，程序判断下一次读取是否经过当前块，如果是，则将缓冲区标记为无效状态(即FF_BUFSTATE_INVALID)。

####  FF_BlockRead()

在FreeRTOS+FAT文件系统中读取数据块的接口函数FF_BlockRead()，其主要作用是读取指定扇区地址的数据块。

首先，从参数pxIOManager指向的IO管理器中检查总扇区数是否已知，如果不为0，则继续执行。其次，根据ulSectorLBA和ulNumSectors计算需要读取的扇区范围，如果超出范围，则返回错误码。接下来，检查读取函数指针是否为空，如果不为空，则调用读取函数进行读取操作。在调用读取函数前会**先检查信号量是否已经被获得**，如果没有被获得则进入阻塞等待状态，直到成功或者出错为止。如果读取函数返回忙碌错误，则等待一段时间后重试，直到读取成功或出错为止。最后，返回读取结果。

```c
if( ( xSemLocked == pdFALSE ) &&
                ( ( pxIOManager->ucFlags & FF_IOMAN_BLOCK_DEVICE_IS_REENTRANT ) == pdFALSE ) )
            {
                FF_PendSemaphore( pxIOManager->pvSemaphore );
            }

            slRetVal = pxIOManager->xBlkDevice.fnpReadBlocks( pxBuffer, ulSectorLBA, ulNumSectors, pxIOManager->xBlkDevice.pxDisk );

            if( ( xSemLocked == pdFALSE ) &&
                ( ( pxIOManager->ucFlags & FF_IOMAN_BLOCK_DEVICE_IS_REENTRANT ) == pdFALSE ) )
            {
                FF_ReleaseSemaphore( pxIOManager->pvSemaphore );
            }
```

##### FF_PendSemaphore( pxIOManager->pvSemaphore ) （在freertos.h中）

一个用于在FreeRTOS中获取信号量的函数FF_PendSemaphore()。该函数将传入的指针pxSemaphore强制转换为信号量句柄，然后调用xSemaphoreTakeRecursive()函数阻塞等待信号量。如果当前调度器状态不是taskSCHEDULER_RUNNING，则直接返回，不需要获取信号量。

其中，xTaskGetSchedulerState()函数用于获取调度器的当前状态，如果调度器处于运行状态，则继续执行。configASSERT(pxSemaphore)用于检查传入的指针是否为空，如果为空则抛出错误。

通过FF_PendSemaphore()函数获取信号量后，可以避免多个任务同时访问共享资源而导致数据竞争的问题，保证数据的正确性和一致性。

```c
void FF_PendSemaphore( void * pxSemaphore )
{
    if( xTaskGetSchedulerState() != taskSCHEDULER_RUNNING )
    {
        /* No need to take the semaphore. */
        return;
    }

    configASSERT( pxSemaphore );
    xSemaphoreTakeRecursive( ( SemaphoreHandle_t ) pxSemaphore, portMAX_DELAY );
}
```

##### FF_ReleaseSemaphore( pxIOManager->pvSemaphore )（在freertos.h中）

一个用于在FreeRTOS中释放信号量的函数FF_ReleaseSemaphore()。该函数将传入的指针pxSemaphore强制转换为信号量句柄，然后调用xSemaphoreGiveRecursive()函数释放信号量。如果当前调度器状态不是taskSCHEDULER_RUNNING，则直接返回，不需要释放信号量。

其中，xTaskGetSchedulerState()函数用于获取调度器的当前状态，如果调度器处于未运行状态，则直接返回。configASSERT(pxSemaphore)用于检查传入的指针是否为空，如果为空则抛出错误。

通过FF_ReleaseSemaphore()函数释放信号量后，可以通知其他任务可以访问共享资源，从而解除之前的阻塞等待并保证任务间协作顺利完成。

##### slRetVal = pxIOManager->xBlkDevice.fnpReadBlocks( pxBuffer, ulSectorLBA, ulNumSectors, pxIOManager->xBlkDevice.pxDisk );

xBlkDevice.fnpReadBlocks是读取硬件block的函数。

在IO管理初始化的时候被赋值为pxParameters->fnReadBlocks;而pxParameters->fnReadBlocks在sddisk中SD卡初始化和挂载时被赋值为prvFFRead，该函数是直接与硬件沟通的函数，用<sd_mmc.h>（SD/MMC 卡驱动库，只需将相应的源文件和头文件添加到项目中即可）在硬件中进行物理读取和写入。

### 小结

