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

For advanced developers, MicroPython is extensive, with low-level C/C++ functions so developers can mix expressive high-level MicroPython code with faster lower-level code, mixing the best of both worlds into one OS.

### Embedded Linux

Website: https://ubuntu.com/embedded

Embedded Linux is built for embedded devices, and it uses a slightly modified version of the Linux kernel. The smaller size and power of Embedded Linux facilitate the integration of all requirements of IoT devices, so you will find that it's useful for navigational devices, tablets, wireless routers, and more.

This is another free, open-source OS that enjoys the support of a large community and many resources that contribute to its development.

The OS takes up a mere 100kb of memory space, making it quick and dynamic, and it also offers an unparalleled level of configuration in the IoT OS scene.

Considered the “Swiss Army Knife” of IoT OSs, **Embedded Linux can be installed on nearly any single-board computer, including Raspberry Pi boards**.

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
| RIOT                 |     Open-source, full multithreading     |                 Can be run as a MacOS process |
| TinyOS               |         C language, open-source          |            Portability across similar devices |
| Windows 10 IoT       |     Proprietary, high-grade security     |     Ideal for heavy-duty industrial use cases |
| OpenWrt              |         Open-source, Linux-based         |                     Primarily used in routers |

## Ideas

1. To realize a smart switch that can be remotely triggered. 
2. Make an RC that can do self-driving or obstacle avoidance. 

## Q

1. What hardware?
2. Complexity?
2. How to minimize the time spent on hardware?
