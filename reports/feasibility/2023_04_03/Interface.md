# Interface

FreeRTOS 可以被认为是一个线程库而不是一个操作系统。

事实上，FreeRTOS 本身根本没有文件系统。 

不过，它拥有众多的附加库，例如 Lab-Project-FreeRTOS-POSIX 与 Lab-Project-FreeRTOS-FAT，其中 Lab-Project-FreeRTOS-POSIX 提供了如何为 C POSIX Library 提供支持的思路。

从 Github 复制这两个库：

```shell
git clone git@github.com:FreeRTOS/Lab-Project-FreeRTOS-POSIX.git 
git clone git@github.com:FreeRTOS/Lab-Project-FreeRTOS-FAT.git 
```

## 已提供的 C POSIX Library 接口

[Lab-Project-FreeRTOS-POSIX](https://www.freertos.org/Documentation/api-ref/POSIX/index.html) 已经提供的 C POSIX Library 有：

- [errno.h](https://www.freertos.org/Documentation/api-ref/POSIX/errno_8h.html): System error numbers.
- [fcntl.h](https://www.freertos.org/Documentation/api-ref/POSIX/fcntl_8h.html): File control options.
- [mqueue.h](https://www.freertos.org/Documentation/api-ref/POSIX/mqueue_8h.html): Message queues.
- [pthread.h](https://www.freertos.org/Documentation/api-ref/POSIX/pthread_8h.html)
- [sched.h](https://www.freertos.org/Documentation/api-ref/POSIX/sched_8h.html)
- [semaphore.h](https://www.freertos.org/Documentation/api-ref/POSIX/semaphore_8h.html)
- [signal.h](https://www.freertos.org/Documentation/api-ref/POSIX/signal_8h.html)
- [sys/types.h](https://www.freertos.org/Documentation/api-ref/POSIX/types_8h.html)
- [time.h](https://www.freertos.org/Documentation/api-ref/POSIX/time_8h.html)
- [unistd.h](https://www.freertos.org/Documentation/api-ref/POSIX/unistd_8h.html)

要在项目中采用 FreeRTOS+POSIX，需要这些头文件以进行移植。

| FreeRTOS platform-specific POSIX configuration               | High-Level Description                                       |
| :----------------------------------------------------------- | :----------------------------------------------------------- |
| [FreeRTOS_POSIX.h](https://www.freertos.org/Documentation/api-ref/POSIX/_free_r_t_o_s___p_o_s_i_x_8h.html). | This header file brings in dependencies required by FreeRTOS+POSIX. This file must be included before all other FreeRTOS+POSIX includes. |
| [FreeRTOS_POSIX_portable_default.h](https://www.freertos.org/Documentation/api-ref/POSIX/_free_r_t_o_s___p_o_s_i_x__portable__default_8h.html) | Defaults for port-specific configuration of FreeRTOS+POSIX.  |
| FreeRTOS_POSIX_portable.h                                    | Port-specific configuration overwrite of FreeRTOS+POSIX. As an example, /lib/FreeRTOS-Plus-POSIX/include/portable/pc/windows/FreeRTOS_POSIX_portable.h, Windows simulator uses the defaults, thus does not need to overwrite anything. |

相似的，若要使用其他 C POSIX Library 中的头文件时，也需要对其进行更改。

事实上，使用 POSIX Library 接口的主要目的是可以更便利地利用已有的在此基础上开发的 C 应用程序。在此项目中，由于只需要完成虚拟文件系统开发以及对文件系统的支持，很少或不涉及移植应用程序，因此不必要考虑进行进一步移植接口。

若必须使用 C POSIX Library，可以参考 `FreeRTOS/FreeRTOS-Kernel/portable/ThirdParty/GCC/Posix/portmacro.h`。

## 现有接口

以下仅为部分可能需要调用的系统函数。这些系统函数足以完成一个简易的虚拟文件系统。但是由于 FreeRTOS 并没有复杂的内存管理机制，故类似 Linux VFS 的一些优化功能可能实现比较困难。

### `pcPortMalloc()` 等

`FreeRTOS/FreeRTOS-Kernel/portable/MemMang/heap_1.c`

```c
void * pvPortMalloc( size_t xWantedSize )
{
  void * pvReturn = NULL;
  static uint8_t * pucAlignedHeap = NULL;

  /* Ensure that blocks are always aligned. */
  #if ( portBYTE_ALIGNMENT != 1 )
  {
      if( xWantedSize & portBYTE_ALIGNMENT_MASK )
      {
          /* Byte alignment required. Check for overflow. */
          if( ( xWantedSize + ( portBYTE_ALIGNMENT - ( xWantedSize & portBYTE_ALIGNMENT_MASK ) ) ) > xWantedSize )
          {
              xWantedSize += ( portBYTE_ALIGNMENT - ( xWantedSize & portBYTE_ALIGNMENT_MASK ) );
          }
          else
          {
              xWantedSize = 0;
          }
      }
  }
  #endif /* if ( portBYTE_ALIGNMENT != 1 ) */

  vTaskSuspendAll();
  {
      if( pucAlignedHeap == NULL )
      {
          /* Ensure the heap starts on a correctly aligned boundary. */
          pucAlignedHeap = ( uint8_t * ) ( ( ( portPOINTER_SIZE_TYPE ) & ucHeap[ portBYTE_ALIGNMENT - 1 ] ) & ( ~( ( portPOINTER_SIZE_TYPE ) portBYTE_ALIGNMENT_MASK ) ) );
      }

      /* Check there is enough room left for the allocation and. */
      if( ( xWantedSize > 0 ) &&                                /* valid size */
          ( ( xNextFreeByte + xWantedSize ) < configADJUSTED_HEAP_SIZE ) &&
          ( ( xNextFreeByte + xWantedSize ) > xNextFreeByte ) ) /* Check for overflow. */
      {
          /* Return the next free byte then increment the index past this
           * block. */
          pvReturn = pucAlignedHeap + xNextFreeByte;
          xNextFreeByte += xWantedSize;
      }

      traceMALLOC( pvReturn, xWantedSize );
  }
  ( void ) xTaskResumeAll();

  #if ( configUSE_MALLOC_FAILED_HOOK == 1 )
  {
      if( pvReturn == NULL )
      {
          vApplicationMallocFailedHook();
      }
  }
  #endif

  return pvReturn;
}
```
`FreeRTOS/FreeRTOS-Kernel/portable/MemMang/heap_2.c`

```C
void vPortFree( void * pv )
{
    uint8_t * puc = ( uint8_t * ) pv;
    BlockLink_t * pxLink;

    if( pv != NULL )
    {
        /* The memory being freed will have an BlockLink_t structure immediately
         * before it. */
        puc -= heapSTRUCT_SIZE;

        /* This unexpected casting is to keep some compilers from issuing
         * byte alignment warnings. */
        pxLink = ( void * ) puc;

        configASSERT( heapBLOCK_IS_ALLOCATED( pxLink ) != 0 );
        configASSERT( pxLink->pxNextFreeBlock == NULL );

        if( heapBLOCK_IS_ALLOCATED( pxLink ) != 0 )
        {
            if( pxLink->pxNextFreeBlock == NULL )
            {
                /* The block is being returned to the heap - it is no longer
                 * allocated. */
                heapFREE_BLOCK( pxLink );
                #if ( configHEAP_CLEAR_MEMORY_ON_FREE == 1 )
                {
                    ( void ) memset( puc + heapSTRUCT_SIZE, 0, pxLink->xBlockSize - heapSTRUCT_SIZE );
                }
                #endif

                vTaskSuspendAll();
                {
                    /* Add this block to the list of free blocks. */
                    prvInsertBlockIntoFreeList( ( ( BlockLink_t * ) pxLink ) );
                    xFreeBytesRemaining += pxLink->xBlockSize;
                    traceFREE( pv, pxLink->xBlockSize );
                }
                ( void ) xTaskResumeAll();
            }
        }
    }
}
```

**Note**: 在 FreeRTOS 内核，有 5 个堆，每个堆各有自己的申请内存空间函数，具体参考：https://www.freertos.org/a00111.html。

### FreeRTOS/FreeRTOS-Kernel/tasks.c

在该文件中，有管理任务的系统函数。

```c
void * pvTaskGetThreadLocalStoragePointer( TaskHandle_t xTaskToQuery,
                                               BaseType_t xIndex )
{
    void * pvReturn = NULL;
    TCB_t * pxTCB;

    if( ( xIndex >= 0 ) &&
        ( xIndex < configNUM_THREAD_LOCAL_STORAGE_POINTERS ) )
    {
        pxTCB = prvGetTCBFromHandle( xTaskToQuery );
        pvReturn = pxTCB->pvThreadLocalStoragePointers[ xIndex ];
    }
    else
    {
        pvReturn = NULL;
    }

    return pvReturn;
}
```

```c
BaseType_t xTaskGetSchedulerState( void )
{
    BaseType_t xReturn;

    if( xSchedulerRunning == pdFALSE )
    {
        xReturn = taskSCHEDULER_NOT_STARTED;
    }
    else
    {
        if( uxSchedulerSuspended == ( UBaseType_t ) pdFALSE )
        {
            xReturn = taskSCHEDULER_RUNNING;
        }
        else
        {
            xReturn = taskSCHEDULER_SUSPENDED;
        }
    }

    return xReturn;
}
```

