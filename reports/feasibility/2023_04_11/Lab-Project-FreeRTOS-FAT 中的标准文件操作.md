# Lab-Project-FreeRTOS-FAT 中的标准文件操作

## Overview

在本文中，将大致介绍 Lab-Project-FreeRTOS-FAT 中的标准文件操作，主要以 ff_fwrite 为例。

`ff_fwrite` 函数定义：

```C
size_t ff_fwrite( const void * pvBuffer,
                  size_t xSize,
                  size_t xItems,
                  FF_FILE * pxStream )
{
    int32_t iReturned;
    size_t xReturn;
    int ff_errno;

    #if ( ffconfigDEV_SUPPORT != 0 )
        if( pxStream->pxDevNode != NULL )
        {
            iReturned = FF_Device_Write( pvBuffer, xSize, xItems, pxStream );
        }
        else
    #endif
    {
        iReturned = FF_Write( pxStream, xSize, xItems, ( uint8_t * ) pvBuffer );
    }

    ff_errno = prvFFErrorToErrno( iReturned );

    if( ff_errno == pdFREERTOS_ERRNO_NONE )
    {
        /* As per the standard fwrite() semantics, the return value is the
         * number of complete items read, which will only equal the number of bytes
         * transferred when the item size is 1. */
        xReturn = ( size_t ) iReturned;
    }
    else
    {
        xReturn = 0;
    }

    /* Store the errno to thread local storage. */
    stdioSET_ERRNO( ff_errno );

    return xReturn;
}
/*-----------------------------------------------------------*/
```

这段代码实现了写入文件的函数 `ff_fwrite`。该函数接受四个参数：要写入的数据的指针 `pvBuffer`，每个数据项的大小 `xSize`，要写入的数据项的数量 `xItems`，以及一个指向要写入的文件的指针 `pxStream`。

函数首先通过判断 `pxStream` 的 `pxDevNode` 是否为 NULL，来确定是使用设备驱动器写入文件还是使用文件系统写入文件。如果 `pxDevNode` 不为 NULL，则说明要写入的文件是设备文件，将调用 `FF_Device_Write` 函数来实现写入。否则将调用 `FF_Write` 函数来实现写入。

函数返回值 `xReturn` 的计算方式符合标准库函数 `fwrite` 的语义。即，如果每个数据项的大小为 1，则返回值是实际写入的字节数；否则返回值是实际写入的完整数据项的数量。

函数最后将发生的错误通过 `prvFFErrorToErrno` 函数转换为标准错误码，并将其存储到线程本地存储中。

## FreeRtos 中 `stdlib.h`

```C
/*
 * File:		stdlib.h
 * Purpose:		Function prototypes for standard library functions
 *
 * Notes:
 */

#ifndef _STDLIB_H
#define _STDLIB_H

/********************************************************************
 * Standard library functions
 ********************************************************************/

int
isspace (int);

int
isalnum (int);

int
isdigit (int);

int
isupper (int);

int
strcasecmp (const char *, const char *);

int
strncasecmp (const char *, const char *, int);

unsigned long
strtoul (char *, char **, int);

int
strlen (const char *);

char *
strcat (char *, const char *);

char *
strncat (char *, const char *, int);

char *
strcpy (char *, const char *);

char *
strncpy (char *, const char *, int);

int
strcmp (const char *, const char *);

int
strncmp (const char *, const char *, int);

void *
memcpy (void *, const void *, unsigned);

void *
memset (void *, int, unsigned);

void
free (void *);
 
void *
malloc (unsigned);

#define RAND_MAX 32767

int
rand (void);

void
srand (int);

/********************************************************************/

#endif
```

这些函数通过最基础的 C 语法实现。

几乎所有文件读写操作都需要这些函数以进行对内存空间的直接控制。

## FF_Write()

位于 `ff_file.c` 中。

```C
/**
 *	@public
 *	@brief	Writes data to a File.
 *
 *	@param	pxFile			FILE Pointer.
 *	@param	ulElementSize		Size of an Element of Data to be copied. (in bytes).
 *	@param	ulCount			Number of Elements of Data to be copied. (ulElementSize * ulCount must not exceed ((2^31)-1) bytes. (2GB). For best performance, multiples of 512 bytes or Cluster sizes are best.
 *	@param	pucBuffer			Byte-wise pucBuffer containing the data to be written.
 *
 * FF_Read() and FF_Write() work very similar. They both complete their task in 5 steps:
 *	1. Write bytes up to a sector border:  FF_WritePartial()
 *	2. Write sectors up to cluster border: FF_BlockWrite()
 *	3. Write complete clusters:            FF_WriteClusters()
 *	4. Write remaining sectors:            FF_BlockWrite()
 *	5. Write remaining bytes:              FF_WritePartial()
 *	@return
 **/
int32_t FF_Write( FF_FILE * pxFile,
                  uint32_t ulElementSize,
                  uint32_t ulCount,
                  uint8_t * pucBuffer )
{
    uint32_t ulBytesLeft = ulElementSize * ulCount;
    uint32_t nBytesWritten = 0;
    uint32_t nBytesToWrite;
    FF_IOManager_t * pxIOManager;
    uint32_t ulRelBlockPos;
    uint32_t ulItemLBA;
    int32_t lResult;
    uint32_t ulSectors;
    uint32_t ulRelClusterPos;
    uint32_t ulBytesPerCluster;
    FF_Error_t xError;

    if( pxFile == NULL )
    {
        xError = ( FF_Error_t ) ( FF_ERR_NULL_POINTER | FF_READ );
    }
    else
    {
        /* Check validity of the handle and the current position within the file. */
        xError = FF_CheckValid( pxFile );

        if( FF_isERR( xError ) == pdFALSE )
        {
            if( ( pxFile->ucMode & FF_MODE_WRITE ) == 0 )
            {
                xError = ( FF_Error_t ) ( FF_ERR_FILE_NOT_OPENED_IN_WRITE_MODE | FF_WRITE );
            }
            /* Make sure a write is after the append point. */
            else if( ( pxFile->ucMode & FF_MODE_APPEND ) != 0 )
            {
                if( pxFile->ulFilePointer < pxFile->ulFileSize )
                {
                    xError = FF_Seek( pxFile, 0, FF_SEEK_END );
                }
            }
        }
    }

    if( FF_isERR( xError ) == pdFALSE )
    {
        pxIOManager = pxFile->pxIOManager;

        /* Open a do{} while( 0 ) loop to allow the use of breaks */
        do
        {
            /* Extend File for at least ulBytesLeft!
             * Handle file-space allocation
             + 1 byte because the code assumes there is always a next cluster */
            xError = FF_ExtendFile( pxFile, pxFile->ulFilePointer + ulBytesLeft + 1 );

            if( FF_isERR( xError ) )
            {
                /* On every error, break from the while( 0 ) loop. */
                break;
            }

            ulRelBlockPos = FF_getMinorBlockEntry( pxIOManager, pxFile->ulFilePointer, 1 ); /* Get the position within a block. */
            ulItemLBA = FF_SetCluster( pxFile, &xError );

            if( FF_isERR( xError ) )
            {
                break;
            }

            if( ( ulRelBlockPos + ulBytesLeft ) <= ( uint32_t ) pxIOManager->usSectorSize )
            {
                /* Bytes to write are within a block and and do not go passed the current block. */
                nBytesWritten = FF_WritePartial( pxFile, ulItemLBA, ulRelBlockPos, ulBytesLeft, pucBuffer, &xError );
                break;
            }

            /*---------- Write (memcpy) to a Sector Boundary. */
            if( ulRelBlockPos != 0 )
            {
                /* Not writing on a sector boundary, at this point the LBA is known. */
                nBytesToWrite = pxIOManager->usSectorSize - ulRelBlockPos;
                nBytesWritten = FF_WritePartial( pxFile, ulItemLBA, ulRelBlockPos, nBytesToWrite, pucBuffer, &xError );

                if( FF_isERR( xError ) )
                {
                    break;
                }

                ulBytesLeft -= nBytesWritten;
                pucBuffer += nBytesWritten;
            }

            /*---------- Write sectors, up to a Cluster Boundary. */
            ulBytesPerCluster = ( pxIOManager->xPartition.ulSectorsPerCluster * pxIOManager->usSectorSize );
            ulRelClusterPos = FF_getClusterPosition( pxIOManager, pxFile->ulFilePointer, 1 );

            if( ( ulRelClusterPos != 0 ) && ( ( ulRelClusterPos + ulBytesLeft ) >= ulBytesPerCluster ) )
            {
                /* Need to get to cluster boundary */
                ulItemLBA = FF_SetCluster( pxFile, &xError );

                if( FF_isERR( xError ) )
                {
                    break;
                }

                ulSectors = pxIOManager->xPartition.ulSectorsPerCluster - ( ulRelClusterPos / pxIOManager->usSectorSize );
                xError = FF_BlockWrite( pxIOManager, ulItemLBA, ulSectors, pucBuffer, pdFALSE );

                if( FF_isERR( xError ) )
                {
                    break;
                }

                nBytesToWrite = ulSectors * pxIOManager->usSectorSize;
                ulBytesLeft -= nBytesToWrite;
                pucBuffer += nBytesToWrite;
                nBytesWritten += nBytesToWrite;
                pxFile->ulFilePointer += nBytesToWrite;

                if( pxFile->ulFilePointer > pxFile->ulFileSize )
                {
                    pxFile->ulFileSize = pxFile->ulFilePointer;
                }
            }

            /*---------- Write entire Clusters. */
            if( ulBytesLeft >= ulBytesPerCluster )
            {
                uint32_t ulClusters;

                FF_SetCluster( pxFile, &xError );

                if( FF_isERR( xError ) )
                {
                    break;
                }

                ulClusters = ( ulBytesLeft / ulBytesPerCluster );

                xError = FF_WriteClusters( pxFile, ulClusters, pucBuffer );

                if( FF_isERR( xError ) )
                {
                    break;
                }

                nBytesToWrite = ulBytesPerCluster * ulClusters;
                ulBytesLeft -= nBytesToWrite;
                pucBuffer += nBytesToWrite;
                nBytesWritten += nBytesToWrite;
                pxFile->ulFilePointer += nBytesToWrite;

                if( pxFile->ulFilePointer > pxFile->ulFileSize )
                {
                    pxFile->ulFileSize = pxFile->ulFilePointer;
                }
            }

            /*---------- Write Remaining Blocks */
            while( ulBytesLeft >= ( uint32_t ) pxIOManager->usSectorSize )
            {
                ulSectors = ulBytesLeft / pxIOManager->usSectorSize;
                {
                    /* HT: I'd leave these pPart/ulOffset for readability... */
                    FF_Partition_t * pPart = &( pxIOManager->xPartition );
                    uint32_t ulOffset = ( pxFile->ulFilePointer / pxIOManager->usSectorSize ) % pPart->ulSectorsPerCluster;
                    uint32_t ulRemain = pPart->ulSectorsPerCluster - ulOffset;

                    if( ulSectors > ulRemain )
                    {
                        ulSectors = ulRemain;
                    }
                }

                ulItemLBA = FF_SetCluster( pxFile, &xError );

                if( FF_isERR( xError ) )
                {
                    break;
                }

                xError = FF_BlockWrite( pxIOManager, ulItemLBA, ulSectors, pucBuffer, pdFALSE );

                if( FF_isERR( xError ) )
                {
                    break;
                }

                nBytesToWrite = ulSectors * pxIOManager->usSectorSize;
                ulBytesLeft -= nBytesToWrite;
                pucBuffer += nBytesToWrite;
                nBytesWritten += nBytesToWrite;
                pxFile->ulFilePointer += nBytesToWrite;

                if( pxFile->ulFilePointer > pxFile->ulFileSize )
                {
                    pxFile->ulFileSize = pxFile->ulFilePointer;
                }
            }

            /*---------- Write (memcpy) Remaining Bytes */
            if( ulBytesLeft == 0 )
            {
                break;
            }

            ulItemLBA = FF_SetCluster( pxFile, &xError );

            if( FF_isERR( xError ) )
            {
                break;
            }

            FF_WritePartial( pxFile, ulItemLBA, 0, ulBytesLeft, pucBuffer, &xError );
            nBytesWritten += ulBytesLeft;
        }
        while( pdFALSE );
    }

    if( FF_isERR( xError ) )
    {
        lResult = xError;
    }
    else
    {
        lResult = ( int32_t ) ( nBytesWritten / ulElementSize );
    }

    return lResult;
} /* FF_Write() */
/*-----------------------------------------------------------*/
```

该函数名为 `FF_Write`，接收四个参数：

1. 一个 `FF_FILE` 类型的指针 `pxFile`，表示要写入数据的文件；
2. 一个 `uint32_t` 类型的变量 `ulElementSize`，表示每个数据元素的大小；
3. 一个 `uint32_t` 类型的变量 `ulCount`，表示要写入的数据元素个数；
4. 一个 `uint8_t` 类型的指针 `pucBuffer`，表示要写入的数据缓冲区。

函数首先会检查传入的文件指针 `pxFile` 是否为空，如果为空则返回一个错误代码。否则，函数会进一步检查文件是否处于正确的模式（写入模式），并判断是否需要将写入位置调整到文件末尾（如果文件处于追加模式且写入位置在文件中间，则需要将写入位置移到文件末尾）。如果一切检查都通过，则会调用一系列子函数来执行实际的写入操作。

在写入过程中，函数会按照一定的策略将数据写入文件中。具体来说，它会首先判断待写入的数据是否可以全部写入当前数据块中。如果可以，则直接调用一个名为 `FF_WritePartial` 的子函数将数据写入该数据块中。如果不行，则需要将数据分成若干个部分，分别写入当前数据块、当前簇（一个簇包含多个数据块）、以及后续的簇中，直到全部写入完成为止。

整个函数的代码比较长，其中包含了不少细节处理和错误处理的代码。它的主要目的是将数据写入文件中，并确保写入操作不会破坏文件的完整性和正确性。

### FF_Write() 调用的函数

以 `FF_WritePartial()` 为例：

```C
static int32_t FF_WritePartial( FF_FILE * pxFile,
                                uint32_t ulItemLBA,
                                uint32_t ulRelBlockPos,
                                uint32_t ulCount,
                                const uint8_t * pucBuffer,
                                FF_Error_t * pxError )
{
    FF_Error_t xError;
    uint32_t ulBytesWritten;

    #if ( ffconfigOPTIMISE_UNALIGNED_ACCESS != 0 )
        {
            BaseType_t xLastRead;

            if( ( ulRelBlockPos + ulCount ) >= ( uint32_t ) pxFile->pxIOManager->usSectorSize )
            {
                /* After this read, ulFilePointer will point to the next block/sector. */
                xLastRead = pdTRUE;
            }
            else
            {
                /* It is not the last read within this block/sector. */
                xLastRead = pdFALSE;
            }

            if( ( ( pxFile->ucState & FF_BUFSTATE_VALID ) == 0 ) &&
                ( ( ulRelBlockPos != 0 ) || ( pxFile->ulFilePointer < pxFile->ulFileSize ) ) )
            {
                xError = FF_BlockRead( pxFile->pxIOManager, ulItemLBA, 1, pxFile->pucBuffer, pdFALSE );
                /* pxFile->ucState will be set later on. */
            }
            else
            {
                xError = FF_ERR_NONE;

                /* the buffer is valid or a whole block/sector will be written, so it is
                 * not necessary to read the contents first. */
            }

            if( FF_isERR( xError ) == pdFALSE )
            {
                memcpy( pxFile->pucBuffer + ulRelBlockPos, pucBuffer, ulCount );

                if( xLastRead == pdTRUE )
                {
                    xError = FF_BlockWrite( pxFile->pxIOManager, ulItemLBA, 1, pxFile->pucBuffer, pdFALSE );
                    pxFile->ucState = FF_BUFSTATE_INVALID;
                }
                else
                {
                    pxFile->ucState |= FF_BUFSTATE_WRITTEN | FF_BUFSTATE_VALID;
                }
            }
            else
            {
                pxFile->ucState = FF_BUFSTATE_INVALID;
            }
        }
    #else /* if ( ffconfigOPTIMISE_UNALIGNED_ACCESS != 0 ) */
        {
            FF_Buffer_t * pxBuffer;

            if( ( ulRelBlockPos == 0 ) && ( pxFile->ulFilePointer >= pxFile->ulFileSize ) )
            {
                /* An entire sector will be written. */
                pxBuffer = FF_GetBuffer( pxFile->pxIOManager, ulItemLBA, FF_MODE_WR_ONLY );
            }
            else
            {
                /* A partial write will be done, make sure to read the contents before
                 * changing anything. */
                pxBuffer = FF_GetBuffer( pxFile->pxIOManager, ulItemLBA, FF_MODE_WRITE );
            }

            if( pxBuffer == NULL )
            {
                xError = ( FF_Error_t ) ( FF_ERR_DEVICE_DRIVER_FAILED | FF_WRITE );
            }
            else
            {
                /* Here we copy to the sector boundary. */
                memcpy( ( pxBuffer->pucBuffer + ulRelBlockPos ), pucBuffer, ulCount );

                xError = FF_ReleaseBuffer( pxFile->pxIOManager, pxBuffer );
            }
        }
    #endif /* if ( ffconfigOPTIMISE_UNALIGNED_ACCESS != 0 ) */

    if( FF_isERR( xError ) == pdFALSE )
    {
        pxFile->ulFilePointer += ulCount;
        ulBytesWritten = ulCount;

        if( pxFile->ulFilePointer > pxFile->ulFileSize )
        {
            pxFile->ulFileSize = pxFile->ulFilePointer;
        }
    }
    else
    {
        ulBytesWritten = 0ul;
    }

    *pxError = xError;

    return ulBytesWritten;
} /* FF_WritePartial() */
/*-----------------------------------------------------------*/
```

这段代码是用于在FatFs文件系统中写入部分数据到文件中的函数 `FF_WritePartial()`。该函数接受一个指向打开的文件的指针 `pxFile`，一个要写入的数据缓冲区指针 `pucBuffer`，以及其他一些参数。该函数的作用是将数据从缓冲区写入到文件中，同时更新文件指针和文件大小。

该函数包含一个条件编译的块，其根据编译时的宏定义，使用不同的写入策略。如果 `ffconfigOPTIMISE_UNALIGNED_ACCESS` 宏定义为非零，则使用优化后的策略，否则使用标准策略。

对于优化策略，首先判断是否需要读取文件块到缓冲区中。如果当前缓冲区无效，或者写入的起始位置不在块的起始位置，或者文件指针指向的位置不在文件的结尾，则需要读取文件块到缓冲区中。如果读取失败，则返回错误。如果读取成功，则将数据复制到缓冲区，并根据是否是块的最后一次写入决定是否将缓冲区的内容写回到存储介质中。如果是最后一次写入，则调用 `FF_BlockWrite()` 函数将缓冲区写入到存储介质中，并将缓冲区标记为无效状态；否则将缓冲区标记为已写入和有效状态。

对于标准策略，首先根据写入的起始位置和文件指针的位置判断是否需要读取文件块到缓冲区中。然后从 `FF_GetBuffer()` 函数中获取一个可写的缓冲区，将数据复制到缓冲区，并调用 `FF_ReleaseBuffer()` 函数释放缓冲区。如果获取缓冲区失败，则返回错误。

最后，如果写入成功，则更新文件指针和文件大小，并将错误代码存储在 `pxError` 指针所指向的位置，并返回实际写入的字节数。否则返回 0。

其中最基础的数据写入 `memcpy()` 定义如下：

```C
void *
memcpy (void *dest, const void *src, unsigned n)
{
	unsigned char *dbp = (unsigned char *)dest;
	unsigned char *sbp = (unsigned char *)src;

	if ((dest != NULL) && (src != NULL) && (n > 0))
	{
      while (n--)
			*dbp++ = *sbp++;
	}
	return dest;
}

/****************************************************************/
```

这段代码是标准库函数 `memcpy()` 的实现。`memcpy()` 函数用于将一段内存的内容复制到另一段内存中，参数包括要复制的目标地址、源地址和要复制的字节数。

该函数首先将目标地址和源地址强制转换为 `unsigned char` 类型的指针，以便逐字节地进行复制。然后它通过一个 `while` 循环将源地址中的内容一个一个字节地复制到目标地址中，直到复制完成。如果目标地址或源地址为 `NULL` 或者要复制的字节数小于等于 0，则不进行复制操作。

最后，函数返回目标地址的指针，表示复制操作已完成。

## FF_Device_Write



函数定义于 `ff_dev_support.c` 中：

```C
size_t FF_Device_Write( const void * pvBuf,
                        size_t lSize,
                        size_t lCount,
                        FF_FILE * pxStream )
{
    lCount *= lSize;

    if( pxStream->pxDevNode != NULL )
    {
        pxStream->pxDevNode->ulFilePointer += lCount;

        if( pxStream->pxDevNode->ulFileLength < pxStream->pxDevNode->ulFilePointer )
        {
            pxStream->pxDevNode->ulFileLength = pxStream->pxDevNode->ulFilePointer;
        }
    }

    return lCount;
}
```

这段代码定义了一个名为 `FF_Device_Write` 的函数，该函数是用于在外部设备上进行写操作的。它有四个参数：指向要写入数据的缓冲区的指针 `pvBuf`，要写入的数据项的大小 `lSize`，要写入的数据项的数量 `lCount`，以及指向表示文件的 `FF_FILE` 结构的指针 `pxStream`。

函数首先将要写入的数据总大小 `lCount` 计算出来，然后检查是否存在外部设备节点。如果指向 `pxStream` 的指针中的 `pxDevNode` 不为 NULL，则表示存在外部设备节点。函数会将设备指针移动到文件中的当前位置加上 `lCount`，以表示下一次写操作应该从哪里开始写入数据。然后函数会检查设备节点中的 `ulFileLength` 是否小于新的文件指针位置。如果是，它会将 `ulFileLength` 设置为新的文件指针位置，以表示文件的大小已经增加。

最后，函数返回 `lCount`，即写入数据的总大小，以指示写操作成功完成。

## FF_Open

另外以下将大致对 `FF_Open` 进行大致介绍。

位于 `ff_file.c` 中。

```C
/**
 *	@public
 *	@brief	Opens a File for Access
 *
 *	@param	pxIOManager	FF_IOManager_t object that was created by FF_CreateIOManager().
 *	@param	pcPath		Path to the File or object.
 *	@param	ucMode		Access Mode required. Modes are a little complicated, the function FF_GetModeBits()
 *	@param	ucMode		will convert a stdio Mode string into the equivalent Mode bits for this parameter.
 *	@param	pxError		Pointer to a signed byte for error checking. Can be NULL if not required.
 *	@param	pxError		To be checked when a NULL pointer is returned.
 *
 *	@return	NULL pointer on error, in which case pxError should be checked for more information.
 *	@return	pxError can be:
 **/
/* *INDENT-OFF* */
#if ( ffconfigUNICODE_UTF16_SUPPORT != 0 )
    FF_FILE * FF_Open( FF_IOManager_t * pxIOManager,
                       const FF_T_WCHAR * pcPath,
                       uint8_t ucMode,
                       FF_Error_t * pxError )
#else
    FF_FILE * FF_Open( FF_IOManager_t * pxIOManager,
                       const char * pcPath,
                       uint8_t ucMode,
                       FF_Error_t * pxError )
#endif
/* *INDENT-ON* */
{
    FF_FILE * pxFile = NULL;
    FF_FILE * pxFileChain;
    FF_DirEnt_t xDirEntry;
    uint32_t ulFileCluster;
    FF_Error_t xError;
    BaseType_t xIndex;
    FF_FindParams_t xFindParams;

    #if ( ffconfigUNICODE_UTF16_SUPPORT != 0 )
        FF_T_WCHAR pcFileName[ ffconfigMAX_FILENAME ];
    #else
        char pcFileName[ ffconfigMAX_FILENAME ];
    #endif

    #if ( ffconfigPROTECT_FF_FOPEN_WITH_SEMAPHORE == 1 )
        {
            if( ( ucMode & FF_MODE_CREATE ) != 0U )
            {
                FF_PendSemaphore( pxIOManager->pvSemaphoreOpen );
            }
        }
    #endif

    memset( &xFindParams, '\0', sizeof( xFindParams ) );

    /* Inform the functions that the entry will be created if not found. */
    if( ( ucMode & FF_MODE_CREATE ) != 0 )
    {
        xFindParams.ulFlags |= FIND_FLAG_CREATE_FLAG;
    }

    if( pxIOManager == NULL )
    {
        /* Use the error function code 'FF_OPEN' as this static
         * function is only called from that function. */
        xError = ( FF_Error_t ) ( FF_ERR_NULL_POINTER | FF_OPEN );
    }

    #if ( ffconfigREMOVABLE_MEDIA != 0 )
        else if( ( pxIOManager->ucFlags & FF_IOMAN_DEVICE_IS_EXTRACTED ) != 0 )
        {
            xError = ( FF_Error_t ) ( FF_ERR_IOMAN_DRIVER_NOMEDIUM | FF_OPEN );
        }
    #endif /* ffconfigREMOVABLE_MEDIA */
    else
    {
        xError = FF_ERR_NONE;

        /* Let xIndex point to the last occurrence of '/' or '\',
         * to separate the path from the file name. */
        xIndex = ( BaseType_t ) STRLEN( pcPath );

        while( xIndex != 0 )
        {
            if( ( pcPath[ xIndex ] == '\\' ) || ( pcPath[ xIndex ] == '/' ) )
            {
                break;
            }

            xIndex--;
        }

        /* Copy the file name, i.e. the string that comes after the last separator. */
        STRNCPY( pcFileName, pcPath + xIndex + 1, ffconfigMAX_FILENAME - 1 );
        pcFileName[ ffconfigMAX_FILENAME - 1 ] = 0;

        if( xIndex == 0 )
        {
            /* Only for the root, the slash is part of the directory name.
             * 'xIndex' now equals to the length of the path name. */
            xIndex = 1;
        }

        /* FF_CreateShortName() might set flags FIND_FLAG_FITS_SHORT and FIND_FLAG_SIZE_OK. */
        FF_CreateShortName( &xFindParams, pcFileName );

        /* Lookup the path and find the cluster pointing to the directory: */
        xFindParams.ulDirCluster = FF_FindDir( pxIOManager, pcPath, xIndex, &xError );

        if( xFindParams.ulDirCluster == 0ul )
        {
            if( ( ucMode & FF_MODE_WRITE ) != 0 )
            {
                FF_PRINTF( "FF_Open[%s]: Path not found\n", pcPath );
            }

            /* The user tries to open a file but the path leading to the file does not exist. */
        }
        else if( FF_isERR( xError ) == pdFALSE )
        {
            /* Allocate an empty file handle and buffer space for 'unaligned access'. */
            pxFile = prvAllocFileHandle( pxIOManager, &xError );
        }
    }

    if( FF_isERR( xError ) == pdFALSE )
    {
        /* Copy the Mode Bits. */
        pxFile->ucMode = ucMode;

        /* See if the file does exist within the given directory. */
        ulFileCluster = FF_FindEntryInDir( pxIOManager, &xFindParams, pcFileName, 0x00, &xDirEntry, &xError );

        if( ulFileCluster == 0ul )
        {
            /* If cluster 0 was returned, it might be because the file has no allocated cluster,
             * i.e. only a directory entry and no stored data. */
            if( STRLEN( pcFileName ) == STRLEN( xDirEntry.pcFileName ) )
            {
                if( ( xDirEntry.ulFileSize == 0 ) && ( FF_strmatch( pcFileName, xDirEntry.pcFileName, ( BaseType_t ) STRLEN( pcFileName ) ) == pdTRUE ) )
                {
                    /* It is the file, give it a pseudo cluster number '1'. */
                    ulFileCluster = 1;
                    /* And reset any error. */
                    xError = FF_ERR_NONE;
                }
            }
        }

        /* Test 'ulFileCluster' again, it might have been changed. */
        if( ulFileCluster == 0ul )
        {
            /* The path is found, but it does not contain the file name yet.
             * Maybe the user wants to create it? */
            if( ( ucMode & FF_MODE_CREATE ) == 0 )
            {
                xError = ( FF_Error_t ) ( FF_ERR_FILE_NOT_FOUND | FF_OPEN );
            }
            else
            {
                ulFileCluster = FF_CreateFile( pxIOManager, &xFindParams, pcFileName, &xDirEntry, &xError );

                if( FF_isERR( xError ) == pdFALSE )
                {
                    xDirEntry.usCurrentItem += 1;
                }
            }
        }
    }

    if( FF_isERR( xError ) == pdFALSE )
    {
        /* Now the file exists, or it has been created.
         * Check if the Mode flags are allowed: */
        if( ( xDirEntry.ucAttrib == FF_FAT_ATTR_DIR ) && ( ( ucMode & FF_MODE_DIR ) == 0 ) )
        {
            /* Not the object, File Not Found! */
            xError = ( FF_Error_t ) ( FF_ERR_FILE_OBJECT_IS_A_DIR | FF_OPEN );
        }
        /*---------- Ensure Read-Only files don't get opened for Writing. */
        else if( ( ( ucMode & ( FF_MODE_WRITE | FF_MODE_APPEND ) ) != 0 ) && ( ( xDirEntry.ucAttrib & FF_FAT_ATTR_READONLY ) != 0 ) )
        {
            xError = ( FF_Error_t ) ( FF_ERR_FILE_IS_READ_ONLY | FF_OPEN );
        }
    }

    if( FF_isERR( xError ) == pdFALSE )
    {
        pxFile->pxIOManager = pxIOManager;
        pxFile->ulFilePointer = 0;

        /* Despite the warning output by MSVC - it is not possible to get here
         * if xDirEntry has not been initialised. */
        pxFile->ulObjectCluster = xDirEntry.ulObjectCluster;
        pxFile->ulFileSize = xDirEntry.ulFileSize;
        pxFile->ulCurrentCluster = 0;
        pxFile->ulAddrCurrentCluster = pxFile->ulObjectCluster;

        pxFile->pxNext = NULL;
        pxFile->ulDirCluster = xFindParams.ulDirCluster;
        pxFile->usDirEntry = xDirEntry.usCurrentItem - 1;
        pxFile->ulChainLength = 0;
        pxFile->ulEndOfChain = 0;
        pxFile->ulValidFlags &= ~( FF_VALID_FLAG_DELETED );

        /* Add pxFile onto the end of our linked list of FF_FILE objects.
         * But first make sure that there are not 2 handles with write access
         * to the same object. */
        FF_PendSemaphore( pxIOManager->pvSemaphore );
        {
            pxFileChain = ( FF_FILE * ) pxIOManager->FirstFile;

            if( pxFileChain == NULL )
            {
                pxIOManager->FirstFile = pxFile;
            }
            else
            {
                for( ; ; )
                {
                    /* See if two file handles point to the same object. */
                    if( ( pxFileChain->ulObjectCluster == pxFile->ulObjectCluster ) &&
                        ( pxFileChain->ulDirCluster == pxFile->ulDirCluster ) &&
                        ( pxFileChain->usDirEntry == pxFile->usDirEntry ) )
                    {
                        /* Fail if any of the two has write access to the object. */
                        if( ( ( pxFileChain->ucMode | pxFile->ucMode ) & ( FF_MODE_WRITE | FF_MODE_APPEND ) ) != 0 )
                        {
                            /* File is already open! DON'T ALLOW IT! */
                            xError = ( FF_Error_t ) ( FF_ERR_FILE_ALREADY_OPEN | FF_OPEN );
                            break;
                        }
                    }

                    if( pxFileChain->pxNext == NULL )
                    {
                        pxFileChain->pxNext = pxFile;
                        break;
                    }

                    pxFileChain = ( FF_FILE * ) pxFileChain->pxNext;
                }
            }
        }

        FF_ReleaseSemaphore( pxIOManager->pvSemaphore );
    }

    if( FF_isERR( xError ) == pdFALSE )
    {
        /* If the file is opened with the truncate flag, truncate its contents. */
        if( ( ucMode & FF_MODE_TRUNCATE ) != 0 )
        {
            /* Set the current size and position to zero. */
            pxFile->ulFileSize = 0;
            pxFile->ulFilePointer = 0;
        }
    }

    if( FF_isERR( xError ) != pdFALSE )
    {
        if( pxFile != NULL )
        {
            #if ( ffconfigOPTIMISE_UNALIGNED_ACCESS != 0 )
                {
                    ffconfigFREE( pxFile->pucBuffer );
                }
            #endif
            ffconfigFREE( pxFile );
        }

        pxFile = NULL;
    }

    #if ( ffconfigPROTECT_FF_FOPEN_WITH_SEMAPHORE == 1 )
        {
            if( ( ucMode & FF_MODE_CREATE ) != 0U )
            {
                FF_ReleaseSemaphore( pxIOManager->pvSemaphoreOpen );
            }
        }
    #endif

    if( pxError != NULL )
    {
        *pxError = xError;
    }

    return pxFile;
} /* FF_Open() */
/*-----------------------------------------------------------*/
```

这段代码定义了一个函数 `FF_Open()`，用于打开一个文件。函数有四个参数：`pxIOManager` 是一个 `FF_IOManager_t` 类型的指针，该类型包含了文件系统的一些参数信息；`pcPath` 是一个字符串，包含了文件的路径；`ucMode` 是一个 `uint8_t` 类型的参数，包含了对文件的访问模式；`pxError` 是一个指向 `FF_Error_t` 类型的指针，用于记录打开文件时可能出现的错误。

在函数的实现过程中，它首先定义了一些变量，包括指向 `FF_FILE` 类型的指针 `pxFile`，用于存储打开的文件的信息；`xFindParams` 是一个 `FF_FindParams_t` 类型的结构体，包含了查找文件所需的一些参数信息；`pcFileName` 是一个字符数组，用于存储文件名。

接着，函数会检查输入参数 `pxIOManager` 是否为 NULL，如果是，函数会将错误码设置为 `FF_ERR_NULL_POINTER | FF_OPEN`。如果 `pxIOManager` 不为 NULL，则函数会继续执行查找目录，创建文件等操作，最后返回一个指向 `FF_FILE` 类型的指针。

### `FF_FILE`

文件打开模式：

```C
/**
 * FF_Open() Mode Information
 * - FF_MODE_WRITE
 *   - Allows WRITE access to the file.
 *   .
 * - FF_MODE_READ
 *   - Allows READ access to the file.
 *   .
 * - FF_MODE_CREATE
 *   - Create file if it doesn't exist.
 *   .
 * - FF_MODE_TRUNCATE
 *   - Erase the file if it already exists and overwrite.
 *   *
 * - FF_MODE_APPEND
 *   - Causes all writes to occur at the end of the file. (Its impossible to overwrite other data in a file with this flag set).
 *   .
 * .
 *
 * Some sample modes:
 * - (FF_MODE_WRITE | FF_MODE_CREATE | FF_MODE_TRUNCATE)
 *   - Write access to the file. (Equivalent to "w").
 *   .
 * - (FF_MODE_WRITE | FF_MODE_READ)
 *   - Read and Write access to the file. (Equivalent to "rb+").
 *   .
 * - (FF_MODE_WRITE | FF_MODE_READ | FF_MODE_APPEND | FF_MODE_CREATE)
 *   - Read and Write append mode access to the file. (Equivalent to "a+").
 *   .
 * .
 * Be careful when choosing modes. For those using FF_Open() at the application layer
 * its best to use the provided FF_GetModeBits() function, as this complies to the same
 * behaviour as the stdio.h fopen() function.
 *
 **/
```

其中 FF_FILE 为相对重要的结构体，定义如下：

```C
typedef struct _FF_FILE
{
    FF_IOManager_t * pxIOManager;  /* Ioman Pointer! */
    uint32_t ulFileSize;           /* File's Size. */
    uint32_t ulObjectCluster;      /* File's Start Cluster. */
    uint32_t ulChainLength;        /* Total Length of the File's cluster chain. */
    uint32_t ulCurrentCluster;     /* Prevents FAT Thrashing. */
    uint32_t ulAddrCurrentCluster; /* Address of the current cluster. */
    uint32_t ulEndOfChain;         /* Address of the last cluster in the chain. */
    uint32_t ulFilePointer;        /* Current Position Pointer. */
    uint32_t ulDirCluster;         /* Cluster Number that the Dirent is in. */
    uint32_t ulValidFlags;         /* Handle validation flags. */

    #if ( ffconfigOPTIMISE_UNALIGNED_ACCESS != 0 )
        uint8_t * pucBuffer; /* A buffer for providing fast unaligned access. */
        uint8_t ucState;     /* State information about the buffer. */
    #endif
    uint8_t ucMode;          /* Mode that File Was opened in. */
    uint16_t usDirEntry;     /* Dirent Entry Number describing this file. */

    #if ( ffconfigDEV_SUPPORT != 0 )
        struct SFileCache * pxDevNode;
    #endif
    struct _FF_FILE * pxNext; /* Pointer to the next file object in the linked list. */
} FF_FILE;
```

这段代码定义了一个名为 `_FF_FILE` 的结构体，该结构体描述了 FatFs 文件系统中打开文件的状态。具体来说，该结构体包含以下字段：

- `pxIOManager`：指向 `FF_IOManager_t` 结构体的指针，用于管理文件系统的输入/输出操作。
- `ulFileSize`：文件的大小，以字节为单位。
- `ulObjectCluster`：文件在文件系统中的起始簇号。
- `ulChainLength`：文件的簇链的总长度，以簇为单位。
- `ulCurrentCluster`：用于防止 FAT 争用的当前簇号。
- `ulAddrCurrentCluster`：当前簇的地址。
- `ulEndOfChain`：簇链中最后一个簇的地址。
- `ulFilePointer`：文件当前读写位置的指针，以字节为单位。
- `ulDirCluster`：描述该文件的目录项所在的簇号。
- `ulValidFlags`：用于验证文件句柄的标志。
- `pucBuffer`：一个用于提供快速非对齐访问的缓冲区（如果启用了非对齐访问优化）。
- `ucState`：关于缓冲区状态的信息（如果启用了非对齐访问优化）。
- `ucMode`：文件的打开模式。
- `usDirEntry`：描述该文件的目录项在目录中的条目号。
- `pxDevNode`：指向 `SFileCache` 结构体的指针，用于管理设备上的文件缓存（如果启用了设备支持）。
- `pxNext`：指向链表中下一个文件对象的指针。