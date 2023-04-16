# RT-Thread DFS 代码
## dfs.h
```cpp
struct dfs_fdtable
{
    uint32_t maxfd;
    struct dfs_file **fds;
};

/* Initialization of dfs */
int dfs_init(void);

char *dfs_normalize_path(const char *directory, const char *filename);
const char *dfs_subdir(const char *directory, const char *filename);

int fd_is_open(const char *pathname);
struct dfs_fdtable *dfs_fdtable_get(void);

void dfs_lock(void);
void dfs_unlock(void);

void dfs_file_lock(void);
void dfs_file_unlock(void);

void dfs_fm_lock(void);
void dfs_fm_unlock(void);

#ifdef DFS_USING_POSIX

/* FD APIs */
int fdt_fd_new(struct dfs_fdtable *fdt);
struct dfs_file *fdt_fd_get(struct dfs_fdtable* fdt, int fd);
void fdt_fd_release(struct dfs_fdtable* fdt, int fd);

int fd_new(void);
struct dfs_file *fd_get(int fd);
void fd_release(int fd);

void fd_init(struct dfs_file *fd);
int fd_associate(struct dfs_fdtable *fdt, int fd, struct dfs_file *file);
int fd_get_fd_index(struct dfs_file *file);

struct dfs_fdtable *dfs_fdtable_get(void);
struct dfs_fdtable *dfs_fdtable_get_global(void);
```

## dfs_file.h
```cpp
struct dfs_file_ops
{
    int (*open)     (struct dfs_file *fd);
    int (*close)    (struct dfs_file *fd);
    int (*ioctl)    (struct dfs_file *fd, int cmd, void *args);
    int (*read)     (struct dfs_file *fd, void *buf, size_t count);
    int (*write)    (struct dfs_file *fd, const void *buf, size_t count);
    int (*flush)    (struct dfs_file *fd);
    int (*lseek)    (struct dfs_file *fd, off_t offset);
    int (*getdents) (struct dfs_file *fd, struct dirent *dirp, uint32_t count);

    int (*poll)     (struct dfs_file *fd, struct rt_pollreq *req);
};

/* file descriptor */
#define DFS_FD_MAGIC     0xfdfd

struct dfs_vnode
{
    uint16_t type;               /* Type (regular or socket) */

    char *path;                  /* Name (below mount point) */
    char *fullpath;              /* Full path is hash key */
    int ref_count;               /* Descriptor reference count */
    rt_list_t list;              /* The node of vnode hash table */

    struct dfs_filesystem *fs;
    const struct dfs_file_ops *fops;
    uint32_t flags;              /* self flags, is dir etc.. */

    size_t   size;               /* Size in bytes */
    void *data;                  /* Specific file system data */
};

struct dfs_file
{
    uint16_t magic;              /* file descriptor magic number */
    uint32_t flags;              /* Descriptor flags */
    int ref_count;               /* Descriptor reference count */
    off_t    pos;                /* Current file position */
    struct dfs_vnode *vnode;     /* file node struct */
    void *data;                  /* Specific fd data */
};

struct dfs_mmap2_args
{
    void *addr;
    size_t length;
    int prot;
    int flags;
    off_t pgoffset;

    void *ret;
};

void dfs_vnode_mgr_init(void);
int dfs_file_is_open(const char *pathname);
int dfs_file_open(struct dfs_file *fd, const char *path, int flags);
int dfs_file_close(struct dfs_file *fd);
int dfs_file_ioctl(struct dfs_file *fd, int cmd, void *args);
int dfs_file_read(struct dfs_file *fd, void *buf, size_t len);
int dfs_file_getdents(struct dfs_file *fd, struct dirent *dirp, size_t nbytes);
int dfs_file_unlink(const char *path);
int dfs_file_write(struct dfs_file *fd, const void *buf, size_t len);
int dfs_file_flush(struct dfs_file *fd);
int dfs_file_lseek(struct dfs_file *fd, off_t offset);

int dfs_file_stat(const char *path, struct stat *buf);
int dfs_file_rename(const char *oldpath, const char *newpath);
int dfs_file_ftruncate(struct dfs_file *fd, off_t length);
int dfs_file_mmap2(struct dfs_file *fd, struct dfs_mmap2_args *mmap2);
```

## dfs_fs.h
```cpp
/* Pre-declaration */
struct dfs_filesystem;
struct dfs_file;

/* File system operations */
struct dfs_filesystem_ops
{
    char *name;
    uint32_t flags;      /* flags for file system operations */

    /* operations for file */
    const struct dfs_file_ops *fops;

    /* mount and unmount file system */
    int (*mount)    (struct dfs_filesystem *fs, unsigned long rwflag, const void *data);
    int (*unmount)  (struct dfs_filesystem *fs);

    /* make a file system */
    int (*mkfs)     (rt_device_t dev_id, const char *fs_name);
    int (*statfs)   (struct dfs_filesystem *fs, struct statfs *buf);

    int (*unlink)   (struct dfs_filesystem *fs, const char *pathname);
    int (*stat)     (struct dfs_filesystem *fs, const char *filename, struct stat *buf);
    int (*rename)   (struct dfs_filesystem *fs, const char *oldpath, const char *newpath);
};

/* Mounted file system */
struct dfs_filesystem
{
    rt_device_t dev_id;     /* Attached device */

    char *path;             /* File system mount point */
    const struct dfs_filesystem_ops *ops; /* Operations for file system type */

    void *data;             /* Specific file system data */
};

/* file system partition table */
struct dfs_partition
{
    uint8_t type;        /* file system type */
    off_t  offset;       /* partition start offset */
    size_t size;         /* partition size */
    rt_sem_t lock;
};

/* mount table */
struct dfs_mount_tbl
{
    const char   *device_name;
    const char   *path;
    const char   *filesystemtype;
    unsigned long rwflag;
    const void   *data;
};

int dfs_register(const struct dfs_filesystem_ops *ops);
struct dfs_filesystem *dfs_filesystem_lookup(const char *path);
const char *dfs_filesystem_get_mounted_path(struct rt_device *device);

int dfs_filesystem_get_partition(struct dfs_partition *part,
                                 uint8_t         *buf,
                                 uint32_t        pindex);

int dfs_mount(const char *device_name,
              const char *path,
              const char *filesystemtype,
              unsigned long rwflag,
              const void *data);
int dfs_unmount(const char *specialfile);

int dfs_mkfs(const char *fs_name, const char *device_name);
int dfs_statfs(const char *path, struct statfs *buffer);
int dfs_mount_device(rt_device_t dev);
int dfs_unmount_device(rt_device_t dev);
```

## dfs_private.h
```cpp
/* extern variable */
extern const struct dfs_filesystem_ops *filesystem_operation_table[];
extern struct dfs_filesystem filesystem_table[];
extern const struct dfs_mount_tbl mount_table[];

extern char working_directory[];
```

## dfs_posix.c
```cpp
int open(const char *file, int flags, ...);
int create(const char *file, mode_t mode);
int close(int fd);
ssize_t read(int fd, void *buf, size_t len);
ssize_t write(int fd, const void *buf, size_t len);
off_t lseek(int fd, off_t offset, int whence); /*return the current read/write position in the file, or -1 on failed.*/
int rename(const char *old_file, const char *new_file);
int unlink(const char *pathname); /*remove*/
int stat(const char *file, struct stat *buf); /* dfs_file_stat(file, buf) */
int fstat(int fildes, struct stat *buf); /* stat(d->vnode->fullpath, buf) */
int fsync(int fildes); /* dfs_file_flush(d) */

/* link to dfs_file.c/dfs_file_x() */
...
```

## fd_get()
```cpp
struct dfs_file *fd_get(int fd)
{
    struct dfs_fdtable *fdt;

    fdt = dfs_fdtable_get();
    return fdt_fd_get(fdt, fd);
}
/**
 * @ingroup Fd
 *
 * This function will return a file descriptor structure according to file
 * descriptor.
 *
 * @return NULL on on this file descriptor or the file descriptor structure
 * pointer.
 */

struct dfs_file *fdt_fd_get(struct dfs_fdtable* fdt, int fd)
{
    struct dfs_file *d;

    if (fd < 0 || fd >= (int)fdt->maxfd)
    {
        return NULL;
    }

    dfs_file_lock();
    d = fdt->fds[fd];

    /* check dfs_file valid or not */
    if ((d == NULL) || (d->magic != DFS_FD_MAGIC))
    {
        dfs_file_unlock();
        return NULL;
    }

    dfs_file_unlock();

    return d;
}
```

## dfs_file_open()
```cpp
int dfs_file_open(struct dfs_file *fd, const char *path, int flags)
{
    struct dfs_filesystem *fs;
    char *fullpath;
    int result;
    struct dfs_vnode *vnode = NULL;
    rt_list_t *hash_head;

    /* parameter check */
    if (fd == NULL)
        return -EINVAL;

    /* make sure we have an absolute path */
    fullpath = dfs_normalize_path(NULL, path);
    if (fullpath == NULL)
    {
        return -ENOMEM;
    }

    LOG_D("open file:%s", fullpath);

    dfs_fm_lock();
    /* vnode find */
    vnode = dfs_vnode_find(fullpath, &hash_head);
    if (vnode)
    {
        vnode->ref_count++;
        fd->pos   = 0;
        fd->vnode = vnode;
        dfs_fm_unlock();
        rt_free(fullpath); /* release path */
    }
    else
    {
        /* find filesystem */
        fs = dfs_filesystem_lookup(fullpath);
        if (fs == NULL)
        {
            dfs_fm_unlock();
            rt_free(fullpath); /* release path */
            return -ENOENT;
        }

        vnode = rt_calloc(1, sizeof(struct dfs_vnode));
        if (!vnode)
        {
            dfs_fm_unlock();
            rt_free(fullpath); /* release path */
            return -ENOMEM;
        }
        vnode->ref_count = 1;

        LOG_D("open in filesystem:%s", fs->ops->name);
        vnode->fs    = fs;             /* set file system */
        vnode->fops  = fs->ops->fops;  /* set file ops */

        /* initialize the fd item */
        vnode->type  = FT_REGULAR;
        vnode->flags = 0;

        if (!(fs->ops->flags & DFS_FS_FLAG_FULLPATH))
        {
            if (dfs_subdir(fs->path, fullpath) == NULL)
                vnode->path = rt_strdup("/");
            else
                vnode->path = rt_strdup(dfs_subdir(fs->path, fullpath));
            LOG_D("Actual file path: %s", vnode->path);
        }
        else
        {
            vnode->path = fullpath;
        }
        vnode->fullpath = fullpath;

        /* specific file system open routine */
        if (vnode->fops->open == NULL)
        {
            dfs_fm_unlock();
            /* clear fd */
            if (vnode->path != vnode->fullpath)
            {
                rt_free(vnode->fullpath);
            }
            rt_free(vnode->path);
            rt_free(vnode);

            return -ENOSYS;
        }

        fd->pos   = 0;
        fd->vnode = vnode;

        /* insert vnode to hash */
        rt_list_insert_after(hash_head, &vnode->list);
    }

    fd->flags = flags;

    if ((result = vnode->fops->open(fd)) < 0)
    {
        vnode->ref_count--;
        if (vnode->ref_count == 0)
        {
            /* remove from hash */
            rt_list_remove(&vnode->list);
            /* clear fd */
            if (vnode->path != vnode->fullpath)
            {
                rt_free(vnode->fullpath);
            }
            rt_free(vnode->path);
            fd->vnode = NULL;
            rt_free(vnode);
        }

        dfs_fm_unlock();
        LOG_D("%s open failed", fullpath);

        return result;
    }

    fd->flags |= DFS_F_OPEN;
    if (flags & O_DIRECTORY)
    {
        fd->vnode->type = FT_DIRECTORY;
        fd->flags |= DFS_F_DIRECTORY;
    }
    dfs_fm_unlock();

    LOG_D("open successful");
    return 0;
}
```