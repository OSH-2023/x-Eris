## 文件缓存的基本信息介绍
- **文件缓存的基本原理：** 文件缓存介于内核的文件操作与底层文件系统之间，就必要性而言，文件缓存是不需要的，但是在实际场景中磁盘访问速度较慢，使用缓存可以有效减少磁盘访问次数，所以文件缓存可以有效提升文件系统的性能。

- **文件缓存的使用场景：** 缓存的有效提升缓存的前提是应用需要反复读取同一批文件。如果应用对数据是「读取一次，然后再也不需要」的访问模式（比如大数据的数据清洗），可以关闭缓存功能，省去缓存不断建立，又反复淘汰的开销。

- **文件缓存的机制介绍：** 文件缓存一般大致可以分为元数据缓存与数据读写缓存
	- **I/O缓存：** 在 I/O 过程中，读取磁盘的速度相对内存读取速度要慢的多。为了提高 I/O 的效率，操作系统会在内存中开辟一块缓冲区，用于暂时存放从磁盘读入或写入磁盘的数据。这个缓冲区就是 IO 缓冲区。
	- **元数据缓存：** 元数据缓存是指在计算机系统中，为了提高文件系统的性能，将文件系统的元数据（如文件名、文件大小、创建时间等）缓存在内存中，以便快速访问。
	- 文件系统使用元数据缓存和I/O缓存的区别在于，缓存I/O使用了操作系统内核缓冲区，在一定程度上分离了应用程序空间和实际的物理设备，可以减少读盘的次数，提高性能。对于读操作来讲，操作系统会先检查内核的缓冲区有没有需要的数据。如果已经缓存了，那就直接从缓存中返回；否则从磁盘中读取，然后缓存在操作系统的缓存中。而元数据缓存是指文件系统为了加速文件系统操作而维护的一个内存缓存，它保存了文件系统中的一些元数据信息，如文件名、文件大小、权限等等。当应用程序需要访问某个文件时，首先会在元数据缓存中查找该文件的元数据信息，如果找到了，则可以直接访问该文件；否则就需要从磁盘上读取该文件的元数据信息，并将其保存到元数据缓存中。

## 文件缓存实现范例
### I/O缓存——Linux文件缓存
- **原理介绍：** Linux的文件缓存是I/O缓存，内核利用一部分物理内存分配出缓冲区，用于缓存系统操作和数据文件。当内核收到读写的请求时，内核先去缓存区找是否有请求的数据，有就直接返回，如果没有则通过驱动程序直接操作磁盘。

#### 代码实现及分析
<font color = RED>以下以最简单的read(), write()为例分析</font>
##### 一、系统调用到FS
```C
SYSCALL_DEFINE3(read, unsigned int, fd, char __user *, buf, size_t, count)
{
	struct fd f = fdget_pos(fd);
......
	loff_t pos = file_pos_read(f.file);
	ret = vfs_read(f.file, buf, count, &pos);
......
}


SYSCALL_DEFINE3(write, unsigned int, fd, const char __user *, buf,
		size_t, count)
{
	struct fd f = fdget_pos(fd);
......
	loff_t pos = file_pos_read(f.file);
    ret = vfs_write(f.file, buf, count, &pos);
......
}

//可以看到，read与write的系统调用是直接调用了vfs_read以及vfs_write
```

```C
ssize_t __vfs_read(struct file *file, char __user *buf, size_t count,
		   loff_t *pos)
{
	if (file->f_op->read)
		return file->f_op->read(file, buf, count, pos);
	else if (file->f_op->read_iter)
		return new_sync_read(file, buf, count, pos);
	else
		return -EINVAL;
}


ssize_t __vfs_write(struct file *file, const char __user *p, size_t count,
		    loff_t *pos)
{
	if (file->f_op->write)
		return file->f_op->write(file, p, count, pos);
	else if (file->f_op->write_iter)
		return new_sync_write(file, p, count, pos);
	else
		return -EINVAL;
}

//对于 read，最终会调用 file->f_op->read 或者 file->f_op->read_iter，对于 write，最终会调用 file->f_op->write 或者 file->f_op->write_iter
```

```C
// 以ext4文件系统为例，文件操作系统集file_operations
const struct file_operations ext4_file_operations = {
......
	.read_iter	= ext4_file_read_iter,
	.write_iter	= ext4_file_write_iter,
......
}

// read write时调用ext4_file_read_iter 和 ext4_file_write_iter
// ext4_file_read_iter 会调用 generic_file_read_iter，ext4_file_write_iter 会调用 __generic_file_write_iter

ssize_t
generic_file_read_iter(struct kiocb *iocb, struct iov_iter *iter)
{
......
    if (iocb->ki_flags & IOCB_DIRECT) {
......
        struct address_space *mapping = file->f_mapping;
......
        retval = mapping->a_ops->direct_IO(iocb, iter);
    }
......
    retval = generic_file_buffered_read(iocb, iter, retval);
}


ssize_t __generic_file_write_iter(struct kiocb *iocb, struct iov_iter *from)
{
......
    if (iocb->ki_flags & IOCB_DIRECT) {
......
        written = generic_file_direct_write(iocb, from);
......
    } else {
......
		written = generic_perform_write(file, from, iocb->ki_pos);
......
    }
}

// 上述generic_file_read_iter 和 __generic_file_write_iter 有相似的逻辑，即判断是否使用缓存，如果设置了IOCB_DIRECT标志就使用直接IO，否则使用缓存IO
```

##### 二、缓存IO的调用
```C
// 带缓存的写函数 generic_perform_write
/*
对每一页，先调用 address_space 的 write_begin 准备
调用 iov_iter_copy_from_user_atomic，将写入的内容从用户空间拷贝到内核空间
调用 address_space 的 write_end 完成写操作
调用 balance_dirty_pages_ratelimited，看脏页是否太多，需要写入硬盘中。脏页的意思是文件内容已写入缓存中，但还没写入硬盘中的页面
*/
ssize_t generic_perform_write(struct file *file,
				struct iov_iter *i, loff_t pos)
{
	struct address_space *mapping = file->f_mapping;
	const struct address_space_operations *a_ops = mapping->a_ops;
	do {
		struct page *page;
		unsigned long offset;	/* Offset into pagecache page */
		unsigned long bytes;	/* Bytes to write to page */
		status = a_ops->write_begin(file, mapping, pos, bytes, flags,
						&page, &fsdata);
		copied = iov_iter_copy_from_user_atomic(page, i, offset, bytes);
		flush_dcache_page(page);
		status = a_ops->write_end(file, mapping, pos, bytes, copied,
						page, fsdata);
		pos += copied;
		written += copied;


		balance_dirty_pages_ratelimited(mapping);
	} while (iov_iter_count(i));
}


/*
在 generic_file_buffered_read 中，首先查找缓存中是否存在相应的缓存页，如果没有找到，不但需要读取这一页的内容，还需要进行预读，这些在 page_cache_sync_readahead 中实现。然后再查找一篇相应的缓存页，这是应该可以找到了

如果缓存中可以找到相应的缓存页，这时候还需要判断是否需要进行预读

最后调用 copy_page_to_iter，将缓存页的内容拷贝回用户内存空间
*/

static ssize_t generic_file_buffered_read(struct kiocb *iocb,
		struct iov_iter *iter, ssize_t written)
{
	struct file *filp = iocb->ki_filp;
	struct address_space *mapping = filp->f_mapping;
	struct inode *inode = mapping->host;
	for (;;) {
		struct page *page;
		pgoff_t end_index;
		loff_t isize;
		page = find_get_page(mapping, index);
		if (!page) {
			if (iocb->ki_flags & IOCB_NOWAIT)
				goto would_block;
			page_cache_sync_readahead(mapping,
					ra, filp,
					index, last_index - index);
			page = find_get_page(mapping, index);
			if (unlikely(page == NULL))
				goto no_cached_page;
		}
		if (PageReadahead(page)) {
			page_cache_async_readahead(mapping,
					ra, filp, page,
					index, last_index - index);
		}
		/*
		 * Ok, we have the page, and it's up-to-date, so
		 * now we can copy it to user space...
		 */
		ret = copy_page_to_iter(page, offset, nr, iter);
    }
}
```

##### 三、缓存IO的实现基础
上面两点分析了从内核为实现read write不断向下调用函数的过程，并在直接IO缓存IO分叉后分析了缓存IO调用时的具体代码，但是问题在于为什么我们能够从缓存区内查找和读写文件，内核究竟是如何实现缓存区以及文件的缓存的呢？
```C
// 以下是文件对象的结构体定义<linux/fs.h>
struct file {

	union {
	
		struct llist_node f_llist;
		
		struct rcu_head f_rcuhead;
		
		unsigned int f_iocb_flags;
	
	};
	
	struct path f_path;
	
	struct inode *f_inode; /* cached value */
	
	const struct file_operations *f_op;
	
	/*
	
	* Protects f_ep, f_flags.
	
	* Must not be taken from IRQ context.
	
	*/
	
	spinlock_t f_lock;
	
	atomic_long_t f_count;
	
	unsigned int f_flags;
	
	fmode_t f_mode;
	
	struct mutex f_pos_lock;
	
	loff_t f_pos;
	
	struct fown_struct f_owner;
	
	const struct cred *f_cred;
	
	struct file_ra_state f_ra;
	
	u64 f_version;
	
	#ifdef CONFIG_SECURITY
	
	void *f_security;
	
	#endif
	
	/* needed for tty driver, and maybe others */
	
	void *private_data;
	
	#ifdef CONFIG_EPOLL
	
	/* Used by fs/eventpoll.c to link all the hooks to this file */
	
	struct hlist_head *f_ep;
	
	#endif /* #ifdef CONFIG_EPOLL */
	
	struct address_space *f_mapping;
	
	errseq_t f_wb_err;
	
	errseq_t f_sb_err; /* for syncfs */

} __randomize_layout

__attribute__((aligned(4))); /* lest something weird decides that 2 is OK */

/* 注意到上述结构中有一个struct address_space *f_mapping
** 这是用于关联文件与内存，其中有一棵树用于关联文件相关的缓存页
** pagecache_get_page 根据 pgoff_t index 这个长整型，在这棵树里面找到缓存页，如果找不到就创建一个缓存页
*/

struct address_space {
	struct inode		*host;		/* owner: inode, block_device */
	struct radix_tree_root	page_tree;	/* radix tree of all pages */
	spinlock_t		tree_lock;	/* and lock protecting it */
......
}

/*调用 iov_iter_copy_from_user_atomic
*/

size_t iov_iter_copy_from_user_atomic(struct page *page,
		struct iov_iter *i, unsigned long offset, size_t bytes)
{
	char *kaddr = kmap_atomic(page), *p = kaddr + offset;
	iterate_all_kinds(i, bytes, v,
		copyin((p += v.iov_len) - v.iov_len, v.iov_base, v.iov_len),
		memcpy_from_page((p += v.bv_len) - v.bv_len, v.bv_page,
				 v.bv_offset, v.bv_len),
		memcpy((p += v.iov_len) - v.iov_len, v.iov_base, v.iov_len)
	)
	kunmap_atomic(kaddr);
	return bytes;
}

/*先将分配好的物理页面通过 kmap_atomic 临时映射到内核虚拟地址空间，然后将用户空间的数据拷贝到内核空间，之后再使用 kunmap_atomic 取消临时映射
*/

// 而后调用read、write

// 最后执行回写脏页
void balance_dirty_pages_ratelimited(struct address_space *mapping)
{
	struct inode *inode = mapping->host;
	struct backing_dev_info *bdi = inode_to_bdi(inode);
	struct bdi_writeback *wb = NULL;
	int ratelimit;
......
	if (unlikely(current->nr_dirtied >= ratelimit))
		balance_dirty_pages(mapping, wb, current->nr_dirtied);
......
}

```


### 元数据缓存——JuiceFS
##### 原理简介
元数据是指从信息资源中抽取出来的用于说明其特征、内容的结构化的数据(如题名,版本、出版数据、相关说明,包括检索点等)，用于组织、描述、检索、保存、管理信息和知识资源。
##### 实现过程简述
内核中可以缓存三种元数据：属性（attribute)、文件项（entry）和目录项（direntry），可以通过以下挂载参数控制缓存时间：
```C
--attr-cache value       属性缓存时长，单位秒 (默认值: 1)
--entry-cache value      文件项缓存时长，单位秒 (默认值: 1)
--dir-entry-cache value  目录项缓存时长，单位秒 (默认值: 1)
```

JuiceFS 客户端在 open() 操作即打开一个文件时，其文件属性（attribute）会被自动缓存在客户端内存中。如果在挂载文件系统时设置了 --open-cache 选项且值大于 0，只要缓存尚未超时失效，随后执行的 getattr() 和 open() 操作会从内存缓存中立即返回结果。

执行 read() 操作即读取一个文件时，文件的 chunk 和 slice 信息会被自动缓存在客户端内存。在缓存有效期内，再次读取 chunk 会从内存缓存中立即返回 slice 信息。

使用 --open-cache 选项设置了缓存时间以后，对于同一个挂载点，当缓存的文件属性发生变化时，缓存会自动失效。但是对于不同的挂载点缓存无法自动失效，因此为了保证强一致性，--open-cache 默认关闭，每次打开文件都需直接访问元数据引擎。如果文件很少发生修改，或者只读场景下（例如 AI 模型训练），则推荐根据情况设置 --open-cache，进一步提高读性能。