---
title: 如何监控Spring Boot应用
author: qinyujun
date: 2020-08-01 15:34:00 +0800
categories: [博客,  笔记]
tags: [Spring Boot, 监控]
toc: true
---

# 如何监控Spring Boot应用

#  关于Spring Boot 应用监控几种方案

## 概述

为什么要对Spring Boot应用进行监控，那是因为一个应用的功能需要同时满足两方面的功能，一个满足业务需求功能，另一个就是非业务功能需求如监控，监控包括很多方面，应用的健康监控，性能指标监控，我上周主要的事情就是玩一遍Springboot的应用的监控，现在就是简单地描述下玩了一遍写一下记录。方便后来的快速上手。

## 初衷

公司的应用部署在GCP(Google Cloud Platform)上，因为公司的安全策略和各种限制，所在在GCP针对监控方面的，是使用了StackDriver来弄，用了它很方便，就能方便在GCP能看到每个VM的表CPU使用情况，还有一些网络请求和磁盘的IO指标数，在这么多的指标的下居然没有JVM的内存使用情况，因为应用曾经出现了两次的OOM， 所以大家都很关注这个Memory使用情况，查看GCP的文档，是要使用JDK 11以上的版本才支持，太不可思议了，就算有别的方案，在公司的条条框框下，想安装什么辅助来监控JVM，估计要折腾个猴年马月， 怎么快怎么来，想到了SpringBoot Actuator，于是开始折腾。

## 方案一

*（Spring Boot Actuator + Spring Boot Admin Client） + Spring Boot Admin Server* 该方案是最简单的，全都是使用Spring官司推荐的组件来弄，所以是只需要简单配置即可

* *Spring Boot Actuator* 它是集成在业务应用里，负责应用的各种指标的收集，并对外暴露Restful 接口

  1. 在业务应用*pom.xml*上加上依赖

  ```xml
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-actuator</artifactId>
      </dependency>
  ```

  2.  加上对外暴露的指标

     ~~~
     management:
       endpoints:
         web:
           exposure:
             include: "*"
     ~~~

     这个对外暴露的接口，有一定的安全风险，需要根据自个情况，请务必做好安全防护

* *Spring Boot Admin Client* 它是集成在业务应用里的，负责把该应用的指标访问地址注册到 *Spring Admin Server*

  1. 在业务应用*pom.xml*加上依赖

     ```xml
        <dependency>
           <groupId>de.codecentric</groupId>
           <artifactId>spring-boot-admin-starter-client</artifactId>
         </dependency>
     ```

  2. 配置*Spring Boot Admin Server*

     ~~~
     spring.boot.admin.client.url=http://localhost:8080
     ~~~

     这个地址就是指向以下介绍的单独的监控应用*Spring Boot Admin Server* 的地址

* *Spring Boot Admin Server* 它是单独的监控应用，在接收到Client注册到Server的指标访问地址后，将定时去访问地址去收集指标数据

  1. 新建应用，依赖里只需要包含Spring Boot Admin 的依赖

     ~~~
     ...
       <dependencies>
         <dependency>
           <groupId>de.codecentric</groupId>
           <artifactId>spring-boot-admin-starter-server</artifactId>
         </dependency>
         <dependency>
           <groupId>org.springframework.boot</groupId>
           <artifactId>spring-boot-starter-test</artifactId>
           <scope>test</scope>
           <exclusions>
             <exclusion>
               <groupId>org.junit.vintage</groupId>
               <artifactId>junit-vintage-engine</artifactId>
             </exclusion>
           </exclusions>
         </dependency>
       </dependencies>
      ...
     ~~~

  2.  请配置端口为8080

  这样就配置完成了，可以直接访问http://localhost:8080  去看看应用的性能指标了

### 该方案的特点

1. 类似注册中心的机制，业务应用只需要配置AdminServer地址就可以了，Admin Server 无需配置所有应用的地址
2. 简单，从数据收集到GUI都是现有的组件，从开发到上线估计不超过半天

## 方案二

*Spring Boot Actuator + （ Spring Cloud Discorvery + Spring Boot Admin Server）* 对比方案一，就是把Spring Admin client 替换为Spring Cloud Discovery 组件，该方案适合于应用的架构是采用微服务架构，存在服务的注册中心，这样Spring Boot Admin Server 就可以可能服务发现组件，拿到所有的服务的访问地址，然后就可以采集指标数据了， 在些不展开描述

效果如下图：

![Spring Boot Admin Server 界面来自于网络](/assets/img/SpringAdmin.png)

## 方案三(推荐)

Spring Boot Actuator + Infux Registry + Influx DB + Grafana，方案对比前两个方案，就是把Spring Boot Admin Server 这个既采集数据和展示替换成了 influx 和Grafana,我是使用该方案，因为公司里都在用这套的方案，然后感觉他们是很好的组合，各自做各自擅长的工作，功能强大，界面漂亮，用过它，就喜欢上了它。

 * 依赖软件

   > 1. InfluxDB 需要先安装
   > 2. Grafana 需要先安装

1. 在业务应用新增Spring Boot Actuator 依赖同上

2. 在业务应用新增registry-influx依赖，它负责推送数据到InfluxDB

   ~~~
   dependency>
     <groupId>io.micrometer</groupId>
     <artifactId>micrometer-core</artifactId>
   </dependency>
   <dependency>
     <groupId>io.micrometer</groupId>
     <artifactId>micrometer-registry-influx</artifactId>
   </dependency>
   ~~~

3. 在业务应用配置InfluxDb 的地址及DB名称

   ~~~
   management.metrics.export.influx.uri=http://localhost:8086
   management.metrics.export.influx.db=带用应用特征的标识如host
   ~~~

   特别要注意*management.metrics.export.influx.db* 这个配置要根据每个实例来特殊化，要不然会出现多个实例都往一个应用influxdb 推数据，会出现数据混乱，可通过在启动脚本里使用-Dmanagement.metrics.export.influx.db来配置

4. 在完成前面三步，可以在influxDB看到推送的数据，然后就可以在Grafana上配置数据源

5. Grafana 有很多分享的漂亮的看板模板，执行拿来主义即可

   效果大概如下：

   ![Grafana效果图，来自于网络](/assets/img/gafrana.png)

## 总结

Influx + Grafana  是个很好方案，Influx可以对指标数据保存起来，不像Admin Server可能一刷新页面就没了指标数据，所以它们更像是Pruduction Ready 的方案。



## 参考

https://docs.spring.io/spring-boot/docs/current/reference/html/production-ready-features.html#production-ready-endpoints-enabling-endpoints