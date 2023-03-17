#hot patch/hotfix
###概念
热修复/热补丁指无需重启程序的情况下对其进行更新。
###可参考方案
* [AndFix](https://github.com/alibaba/AndFix)
    直接在native层进行方法的结构体信息对换，从而实现放方法新旧替换，从而实现hotfix功能。
* [dexposed](https://github.com/alibaba/dexposed)
    基于xposed框架实现的安卓平台上的无侵入式运行时AOP框架，支持函数级别的在线热更新。
* [Tinker](https://github.com/Tencent/tinker)  

* WaxPatch
    通过Lua语言编写的iOS框架，使用 OC runtime 特性调用替换应用程序内部由 OC 编写的类方法，达到HotFix的目的。
* [JSPatch](https://github.com/bang590/JSPatch)
    在项目中引入JSPatch引擎，实现用JavaScript语言调用Objective-C的原生接口，获得脚本语言的能力：动态更新iOS APP，替换项目原生代码。
* [kpatch](https://github.com/dynup/kpatch)
    在linux系统中针对于内核的hotfix方案。

###以往课题
####OSH-2018/X-yeahtiger
#####实现思路
* 控制 main 进程进入修复代码片段
* 在修复代码片段中获得全局变量、函数的引用信息和新旧函数的地址
* 将旧函数入口处替换为对新函数的跳转
* 恢复现场，完成热替换
#####可优化的点
* 原方案获取全局变量等信息时效率过低，可采用内核态获取工作进程控制权，减少开销。
* 代码替换采用替换旧函数入口处代码为作为新函数跳转，效率较低。可在此方面进行优化
* 该方案的热修复只能处理无状态模块。可实现对有状态模块的热修复。