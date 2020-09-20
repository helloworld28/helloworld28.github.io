---
title: 一致性协议
author: powerjun        
date: 2020-08-15 09:14:00 +0800
categories: [博客,  笔记]
tags: [一致性协议]
toc: true
---

### 概述

说到分布式系统，就必须说到一致性协议，经常在看一些技术的文章或者看一些框架都会提到所采用的一致性协议，像有数据事务用到的2PC，3PC，Paxos协议，ZooKeeper的ZAB协议，阿里的相关产品用到的Raft协议，还有个人用到Akka的Cluster所采用的Gossip协议，现在就对这些一致性协议做一些总结。

