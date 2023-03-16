# Operating System for IoT

## Category

[toc]

## What Is an IoT Operating System?

Operating systems that are written for the Internet of Things are especially designed to perform within the strict constraints of small IoT devices.

These are *embedded* operating systems that enable IoT devices to communicate with cloud services and other IoT devices over a global network and can do so within the tight parameters of limited amounts of memory and processing power.

The beauty of these operating systems lies in the opportunities they provide with IoT devices, such as remote data management, cellular connectivity, and more.

In the era of digitization, many aspects of people’s lives are being significantly improved by remotely controllable devices & whole infrastructures — the so-called Internet of Things.

This industry is continually growing & bringing new products: a nearly $250B market is projected to have grown by no less than 5 times by 2027.

## Available Choices for IoT

### AWS FreeRTOS

Website: https://www.freertos.org/

The official tuturiol:  [Mastering_the_FreeRTOS_Real_Time_Kernel-A_Hands-On_Tutorial_Guide.pdf](../ref/Mastering_the_FreeRTOS_Real_Time_Kernel-A_Hands-On_Tutorial_Guide.pdf) 

Also referred to as “Amazon FreeRTOS,” this operating system was invented *by* Amazon and made an open-source, microcontroller-based operating system that has rapidly become a benchmark IoT OS within the last few years.

FreeRTOS uses Amazon Web Services (AWS IoT Core) to run IoT applications and has a particularly small memory footprint (only 6-15kb) making it a more adaptable small powered microcontroller. 

Developers can rest easy knowing that Amazon invested heavily in the development of IoT data security as well.

### Contiki

Website: https://www.contiki-ng.org/

Making its debut in 2003, Contiki is an operating system often compared to Microsoft Windows and Linux, but it was designed with a special focus on the nuances of networked, memory-constrained systems (i.e. most IoT devices).

Contiki is an open-source OS most renowned for its ability to easily connect very small, economical, and low-powered microcontrollers to the Internet.

The operating system has a reputation of being exceptionally useful in building complex wireless systems, as well as being highly memory-efficient. 

It also suits both business and non-business use cases.

### Mbed OS

Website: https://os.mbed.com/mbed-os/

Mbed OS is a free, open-source operating system widely recognized for its usage of an ARM processor and for offering a wide array of connectivity options that developers can play around with, including WiFi and Bluetooth.

Mbed OS's multilayer security protocols are what makes it such an appealing system for developers looking to get started with IoT projects.

One benefit that developers enjoy with Mbed OS is that it keeps their code clean and portable, as well as the ability to make a prototype of IoT applications with the use of ARM cortex M-based devices.

**At present, more than 150 boards are supported.**

### MicroPython

Website: https://micropython.org/

MicroPython is a very compact, open-source reimplementation of the Python programming language with a focus on microcontrollers.

The language is more useful to beginners than other languages, while still being robust enough for industrial use. Also, standard Python is applicable.

An advantage of MicroPython is that it allows developers to rapidly evolve from learning the basics to implementing real project code.

For advanced developers, MicroPython is extensive, with low-level C/C++ functions so developers can mix expressive high-level MicroPython code with faster lower level code, mixing the best of both worlds into one OS.

### Embedded Linux

Website: https://ubuntu.com/embedded

Embedded Linux is built for embedded devices, and it uses a slightly-modified version of the Linux kernel. The smaller size and power of Embedded Linux facilitates the integration of all requirements of IoT devices, so you will find that it's useful for navigational devices, tablets, wireless routers, and more.

This is another free, open-source OS that enjoys the support of a large community and many resources that contribute to its development.

The OS takes up a mere 100kb of memory space, making it quick and dynamic, and it also offers an unparalleled level of configuration in the IoT OS scene.

Considered the “Swiss Army Knife” of IoT OSs, **Embedded Linux can be installed on nearly any single board computer, including Raspberry Pi boards**.

### RIOT

Website: https://www.riot-os.org/

Often considered to be the Linux of the IoT world, RIOT is another open-source operating system specialized for IoT devices. Newcomers with previous Linux experience will find achieving results with this OS to be quite simple.

RIOT supports full multithreading and SSL/TSL libraries, and facilitates the usage of 8, 16, and 32-bit processors. **Lastly, there is a port of this OS that makes it possible to run as a Linux or macOS process.**

### Windows 10 IoT

Website: https://developer.microsoft.com/en-us/windows/iot/

Windows 10 IoT is simply a component of the Microsoft Windows 10 operating system, but it is designed with IoT devices in mind.

An interesting fact is that this OS is divided into two parts:

1. One is Windows 10 IoT Core which is designed to support small embedded devices (covers 80%+ of use cases);

2. The other is Windows 10 IoT Enterprise designed to support heavy-duty industrial applications with high-grade reliability in mind.

Windows 10 IoT Core offers a familiar interface, has better user control than other OSs, and is accepted among the IoT community as being a powerful IoT operating system.

Win 10 IoT is especially useful with the Raspberry PI board series and with the Grove Kit for Win10 IoT Core & Azure platform.

### TinyOS

Website: http://www.tinyos.net/

TinyOS is a component-based open-source operating system. “nesC” is the core language of TinyOS, which is a dialect of the C programming language.

This operating system enjoys large support among the development community because of how it optimizes the memory of IoT devices and how the OS tends not to overload IoT devices. One key advantage is transferability:

**A TinyOS program can be reusable on other devices if the code need not be changed because of the similarity of the devices.**

### OpenWrt

Website: https://openwrt.org/

OpenWrt is another open-source option based on Linux and has a strong presence in routers. **At present, more than 200 board variations ship with OpenWRT.**

The OS has a reputation for preventing security breaches and enjoys the support of a committed base of developers constantly improving it.

OpenWrt is also a highly-customizable OS since it contains the full features of Linux. While OpenWrt has a strong presence in routing equipment, it has slowly permeated other IoT devices with an excellent record of success.

### Quick Comparison

| IoT Operating System |                 Features                 |                                     Use cases |
| :------------------- | :--------------------------------------: | --------------------------------------------: |
| Contiki NG           |            Open-source, free             |          Networked memory-constrained systems |
| FreeRTOS             |   Open-source, free, uses AWS IoT Core   |           Devices with tiny amounts of memory |
| Mbed OS              |      ARM-based, high-grade security      |                             For portable code |
| MicroPython          | Uses standard Python, easy to learn, C++ |                              Rapid deployment |
| Embedded Linux       |            Linux kernel, free            | Versatile - can be used for various use cases |
| RIOT                 |     Open-source, full multithreading     |                   Can be run as MacOS process |
| TinyOS               |         C language, open-source          |            Portability across similar devices |
| Windows 10 IoT       |     Proprietary, high-grade security     |     Ideal for heavy-duty industrial use cases |
| OpenWrt              |         Open-source, Linux-based         |                     Primarily used in routers |

## Idea

To realize a smart switch that can be remotely triggered. 

## Q

1. What hardware?
2. Complexity?

-------------

--------------------------

**中文为谷歌翻译，非常不准，请参考英文。**

## 什么是物联网操作系统？

为物联网编写的操作系统专门设计用于在小型物联网设备的严格限制内运行。

这些是*嵌入式*操作系统，使物联网设备能够通过全球网络与云服务和其他物联网设备进行通信，并且可以在有限的内存和处理能力的严格参数范围内进行通信。

这些操作系统的美妙之处在于它们为物联网设备提供了机会，例如远程数据管理、蜂窝连接等。

在数字化时代，人们生活的许多方面都通过远程控制设备和整个基础设施——即所谓的物联网——得到了显着改善。

这个行业正在不断发展并带来新产品：到 2027 年，一个近 $250B 的市场预计增长不少于 5 倍。

## 物联网的可用选择

### AWS FreeRTOS

网站：https://www.freertos.org/

官方教程：[Mastering_the_FreeRTOS_Real_Time_Kernel-A_Hands-On_Tutorial_Guide.pdf](../ref/Mastering_the_FreeRTOS_Real_Time_Kernel-A_Hands-On_Tutorial_Guide.pdf)

该操作系统也称为“Amazon FreeRTOS”，*由* Amazon 发明，并制作了一个基于微控制器的开源操作系统，在过去几年内迅速成为基准物联网操作系统。

FreeRTOS 使用 Amazon Web Services (AWS IoT Core) 来运行 IoT 应用程序，并且具有特别小的内存占用空间（仅 6-15kb），使其成为适应性更强的小型微控制器。

开发人员可以高枕无忧，因为他们知道亚马逊也在物联网数据安全开发方面投入了大量资金。

### 康蒂基

网站：https://www.contiki-ng.org/

Contiki 于 2003 年首次亮相，是一种经常与 Microsoft Windows 和 Linux 相提并论的操作系统，但它的设计特别关注网络、内存受限系统（即大多数物联网设备）的细微差别。

Contiki 是一种开放源代码操作系统，以其能够轻松地将非常小、经济且低功耗的微控制器连接到 Internet 的能力而闻名。

该操作系统在构建复杂的无线系统方面非常有用，而且内存效率高，因此享有盛誉。

它还适用于商业和非商业用例。

### mbed操作系统

网站：https://os.mbed.com/mbed-os/

Mbed OS 是一款免费的开源操作系统，因其使用 ARM 处理器以及提供开发人员可以使用的各种连接选项（包括 WiFi 和蓝牙）而广受认可。

Mbed OS 的多层安全协议使其成为对希望开始 IoT 项目的开发人员如此有吸引力的系统。

开发人员享受 Mbed OS 的一个好处是它使他们的代码保持清洁和可移植性，以及使用基于 ARM cortex M 的设备制作物联网应用程序原型的能力。

**目前支持超过150个板卡**

### 微丝

网站：https://micropython.org/

MicroPython 是 Python 编程语言的一种非常紧凑的开源重新实现，专注于微控制器。

该语言比其他语言对初学者更有用，同时仍然足够强大以供工业使用。 此外，标准 Python 也适用。

MicroPython 的一个优点是它允许开发人员从学习基础知识快速发展到实现真正的项目代码。

对于高级开发人员，MicroPython 功能广泛，具有低级 C/C++ 函数，因此开发人员可以将富有表现力的高级 MicroPython 代码与速度更快的低级代码混合在一起，将两全其美的功能融合到一个操作系统中。

### 嵌入式 Linux

网站：https://ubuntu.com/embedded

嵌入式 Linux 是为嵌入式设备构建的，它使用略微修改过的 Linux 内核版本。 嵌入式 Linux 更小的尺寸和更强大的功能有助于集成物联网设备的所有需求，因此您会发现它对导航设备、平板电脑、无线路由器等非常有用。

这是另一个免费的开源操作系统，它得到了大型社区的支持和有助于其开发的许多资源。

该操作系统仅占用 100kb 的内存空间，使其快速且动态，并且还提供了物联网操作系统场景中无与伦比的配置级别。

被视为物联网操作系统的“瑞士军刀”，**嵌入式 Linux 几乎可以安装在任何单板计算机上，包括 Raspberry Pi 板**。

### 骚乱

网站：https://www.riot-os.org/

RIOT 通常被认为是物联网世界的 Linux，是另一个专门用于物联网设备的开源操作系统。 以前有 Linux 经验的新手会发现使用这个操作系统取得成果非常简单。

RIOT 支持完整的多线程和 SSL/TSL 库，并促进 8、16 和 32 位处理器的使用。 **最后，这个操作系统有一个端口，可以作为 Linux 或 macOS 进程运行。**

### Windows 10 物联网

网站：https://developer.microsoft.com/en-us/windows/iot/

Windows 10 IoT 只是 Microsoft Windows 10 操作系统的一个组件，但它在设计时就考虑到了 IoT 设备。

一个有趣的事实是，该操作系统分为两部分：

1. 一个是 Windows 10 IoT 核心版，旨在支持小型嵌入式设备（涵盖 80%+ 的用例）；
2. 另一个是 Windows 10 IoT Enterprise，旨在支持重型工业应用，同时考虑到高可靠性。

Windows 10 IoT Core 提供了熟悉的界面，比其他操作系统具有更好的用户控制，并且被物联网社区接受为一个强大的物联网操作系统。

Win 10 IoT 尤其适用于 Raspberry PI 板系列以及适用于 Win10 IoT Core 和 Azure 平台的 Grove 套件。

### TinyOS

网站：http://www.tinyos.net/

TinyOS 是一个基于组件的开源操作系统。 “nesC”是TinyOS的核心语言，是C编程语言的一种方言。

该操作系统在开发社区中享有广泛的支持，因为它优化了物联网设备的内存，并且操作系统不会使物联网设备过载。 一个关键优势是可转移性：

**如果由于设备的相似性而无需更改代码，则 TinyOS 程序可以在其他设备上重复使用。**

### OpenWrt

网站：https://openwrt.org/

OpenWrt 是另一个基于 Linux 的开源选项，在路由器中占有重要地位。 **目前，OpenWRT 附带了 200 多种板卡变体。**

该操作系统以防止安全漏洞而著称，并得到了一群忠诚的开发人员的支持，他们不断改进它。

OpenWrt 也是一个高度可定制的操作系统，因为它包含了 Linux 的全部功能。 虽然 OpenWrt 在路由设备中占有一席之地，但它已慢慢渗透到其他物联网设备中，并取得了出色的成功记录。

### 快速比较

| 物联网操作系统    |             特点              |                    用例 |
| :---------------- | :---------------------------: | ----------------------: |
| Contiki NG        |          开源，免费           |        网络内存受限系统 |
| 免费RTOS          | 开源、免费、使用 AWS IoT Core |      具有少量内存的设备 |
| 操作系统          |     基于 ARM 的高级安全性     |          对于可移植代码 |
| 微型蟒蛇          | 使用标准Python，简单易学，C++ |                快速部署 |
| 嵌入式Linux       |       Linux 内核，免费        | 多功能 - 可用于各种用例 |
| 防暴              |      开源、完整的多线程       | 可以作为 MacOS 进程运行 |
| 微操作系统        |         C 语言，开源          |    跨类似设备的可移植性 |
| Windows 10 物联网 |       专有的高级安全性        |  重型工业用例的理想选择 |
| 开放世界          |       开源，基于 Linux        |          主要用于路由器 |

## 主意

实现可远程触发的智能开关。

## 问

1. 什么硬件？
2.复杂性？