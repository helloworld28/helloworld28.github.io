---
title: Redis 集群（三主三从）快速搭建
author: powerjun        
date: 2021-05-03 22:38:00 +0800
categories: [笔记,  技术杂记]
tags: [redis]
toc: false
---
在学习Redis 的过程中， 很多博客教程中涉及到搭建Redis 集群（三主三从）到一台机上去做测试时，我是按照教程去去操作，后面可能是因为版本的一些问题，我就找到官方的文档去看，发现官方的文档介绍已经很具体了，而且有非常快捷的方式去在一台机搭建一个三主三从的集群，已经存在对应的shell 脚本了，直接运行就有了。

### 安装Redis 

```
$ wget https://download.redis.io/releases/redis-6.2.2.tar.gz
$ tar xzf redis-6.2.2.tar.gz
$ cd redis-6.2.2
$ make
```

这个安装步骤和其他教程一样的，下载安装后，然后解压编译，如果编译失败请检查gcc 环境

其中快捷操作的脚本就在 utils/create-cluster 目录里

### 启动集群的六个节点

进入目录 utils/create-cluster 运行以下命令，它就会启动了六个Redis server 进程，端口分别是 [30001 ~ 30006]

```
[vagrant@localhost create-cluster]$ ./create-cluster start
Starting 30001
Starting 30002
Starting 30003
Starting 30004
Starting 30005
Starting 30006
[vagrant@localhost create-cluster]$ ps -ef|grep redisr 
vagrant   7589     1  0 14:06 ?        00:00:00 ../../src//redis-server *:30001 [cluster]
vagrant   7591     1  0 14:06 ?        00:00:00 ../../src//redis-server *:30002 [cluster]
vagrant   7597     1  0 14:06 ?        00:00:00 ../../src//redis-server *:30003 [cluster]
vagrant   7603     1  0 14:06 ?        00:00:00 ../../src//redis-server *:30004 [cluster]
vagrant   7613     1  0 14:06 ?        00:00:00 ../../src//redis-server *:30005 [cluster]
vagrant   7615     1  0 14:06 ?        00:00:00 ../../src//redis-server *:30006 [cluster]

```

### 配置集群

接着要把六个节点分成三组形成三主三从的结构，运行 `create-cluster create` 然后输入 `yes`, 然后就可以

```
[vagrant@localhost create-cluster]$ ./create-cluster create
>>> Performing hash slots allocation on 6 nodes...
Master[0] -> Slots 0 - 5460
Master[1] -> Slots 5461 - 10922
Master[2] -> Slots 10923 - 16383
Adding replica 127.0.0.1:30005 to 127.0.0.1:30001
Adding replica 127.0.0.1:30006 to 127.0.0.1:30002
Adding replica 127.0.0.1:30004 to 127.0.0.1:30003
>>> Trying to optimize slaves allocation for anti-affinity
[WARNING] Some slaves are in the same host as their master
M: f4e013730b804fa7e219b402fcc6c1b5a539895c 127.0.0.1:30001
   slots:[0-5460] (5461 slots) master
M: 869060e81eb544ec5169102845c7cb334af480d5 127.0.0.1:30002
   slots:[5461-10922] (5462 slots) master
M: fe6d10b6f896e02e2e041387a64b8f60a1ab2383 127.0.0.1:30003
   slots:[10923-16383] (5461 slots) master
S: f389372150588f82e7413dc69f5649dbec9e8584 127.0.0.1:30004
   replicates f4e013730b804fa7e219b402fcc6c1b5a539895c
S: e05a1618d89fc34e2f07a7664c8712b84367cf51 127.0.0.1:30005
   replicates 869060e81eb544ec5169102845c7cb334af480d5
S: a9d8c49b72b309bdfe2e35e81ae6712edb84ae14 127.0.0.1:30006
   replicates fe6d10b6f896e02e2e041387a64b8f60a1ab2383
Can I set the above configuration? (type 'yes' to accept): yes
>>> Nodes configuration updated
>>> Assign a different config epoch to each node
>>> Sending CLUSTER MEET messages to join the cluster
Waiting for the cluster to join

>>> Performing Cluster Check (using node 127.0.0.1:30001)
M: f4e013730b804fa7e219b402fcc6c1b5a539895c 127.0.0.1:30001
   slots:[0-5460] (5461 slots) master
   1 additional replica(s)
S: f389372150588f82e7413dc69f5649dbec9e8584 127.0.0.1:30004
   slots: (0 slots) slave
   replicates f4e013730b804fa7e219b402fcc6c1b5a539895c
S: a9d8c49b72b309bdfe2e35e81ae6712edb84ae14 127.0.0.1:30006
   slots: (0 slots) slave
   replicates fe6d10b6f896e02e2e041387a64b8f60a1ab2383
S: e05a1618d89fc34e2f07a7664c8712b84367cf51 127.0.0.1:30005
   slots: (0 slots) slave
   replicates 869060e81eb544ec5169102845c7cb334af480d5
M: 869060e81eb544ec5169102845c7cb334af480d5 127.0.0.1:30002
   slots:[5461-10922] (5462 slots) master
   1 additional replica(s)
M: fe6d10b6f896e02e2e041387a64b8f60a1ab2383 127.0.0.1:30003
   slots:[10923-16383] (5461 slots) master
   1 additional replica(s)
[OK] All nodes agree about slots configuration.
>>> Check for open slots...
>>> Check slots coverage...
[OK] All 16384 slots covered.

```

### 检查集群状态

```
[vagrant@localhost create-cluster]$ redis-cli -c -p 30001
127.0.0.1:30001> cluster nodes
f389372150588f82e7413dc69f5649dbec9e8584 127.0.0.1:30004@40004 slave f4e013730b804fa7e219b402fcc6c1b5a539895c 0 1620050968155 1 connected
a9d8c49b72b309bdfe2e35e81ae6712edb84ae14 127.0.0.1:30006@40006 slave fe6d10b6f896e02e2e041387a64b8f60a1ab2383 0 1620050968054 3 connected
e05a1618d89fc34e2f07a7664c8712b84367cf51 127.0.0.1:30005@40005 slave 869060e81eb544ec5169102845c7cb334af480d5 0 1620050968054 2 connected
869060e81eb544ec5169102845c7cb334af480d5 127.0.0.1:30002@40002 master - 0 1620050968054 2 connected 5461-10922
fe6d10b6f896e02e2e041387a64b8f60a1ab2383 127.0.0.1:30003@40003 master - 0 1620050968054 3 connected 10923-16383
f4e013730b804fa7e219b402fcc6c1b5a539895c 127.0.0.1:30001@40001 myself,master - 0 1620050968000 1 connected 0-5460

```



参考：

https://redis.io/topics/cluster-tutorial