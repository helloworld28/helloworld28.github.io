---
title: bootstrap-table group-by-v2 的使用
author: powerjun        
date: 2021-09-19 21:38:00 +0800
categories: [笔记,  技术杂记]
tags: [bootstrap-table, 前端]
toc: false
---
#  bootstrap-table group-by-v2 的使用

在帮忙在做朋友的项目时，自己搭建的项目，因为项目比较小，暂时一个开发，所以没有用前后端分离的框架来用，是直接使用了`ruoyi` 开源框架，这个框架的前端就直接封装了使用了`bootstrap-table`, 然后其中一个需求就是前端表格要显示合计行，而且这个合计不是所以记录的合计，要是全部记录的合计还好，boostrap-table, 本身就有一个footer 字段来支持这个合计，但需求要的是对记录列表进行分组然后进行分组合计，找来找去就感觉这个其中一个国人开发的一个`boostrap-table`插件 `group-by-v2` 可以满足需求。

这个插件的例子效果，就是想要的，但是把它用起来真的花了不少心思，因为官方给的使用说明简单得就像没有一样，就感觉作者是直接给你一个例子，自己去琢磨，在实际使用过程中，还真的要靠分析它的源码和bootstrap-table 的源码才知道其中原因，最后才把问题解决，感触颇深，所以把其中对它的使用过程，记录一下，为了以后还可以想起来有这些坑在里面。

## 吐槽官方指南：

https://www.bootstrap-table.com.cn/doc/extensions/group-by-v2/

![boostrap-table-official-guide](/assets/img/Snipaste_2021-09-19_21-27-21.png)

不得不吐槽一下，简单得离谱，这个也太懒了，很影响大家对它的使用。

## 我的使用步骤：

1. 下载 `bootstrap-table` 与 `bootstrap-table-group-by-v2` 插件 js 和 css 文件

   **一定要注意它们之前的版本一定要一致，否则会提示属性找不到的错误**

   下载地址：

   https://unpkg.com/bootstrap-table@1.18.3/dist/bootstrap-table.min.css

   https://unpkg.com/bootstrap-table@1.18.3/dist/bootstrap-table.min.js

   https://unpkg.com/bootstrap-table@1.18.3/dist/extensions/group-by-v2/bootstrap-table-group-by.min.js

   https://unpkg.com/bootstrap-table@1.18.3/dist/extensions/group-by-v2/bootstrap-table-group-by.css

2.  引入它们的到页面里，并在bootstrap-table的配置里加上相关参数：

   ```
    groupBy: "true",
    groupByField: ["itemNo", "colorCode"],
    groupByFormatter: function(value, idx, data){
    return  value + ", 报数合计：" + sumQuote(data);
    }
   ```

   

3. 需要设置 `bootstrap-table` 分页的模式`sidePagination`为client

   就是这个问题花不我不少时间去排查，因为ruoyi 框架默认值为server 所以一直有问题，因为要给前端对数据进行分组，那就要拿到全部的数据，所以也能理解，但使用指南一点都不提这点，

   ![boostrap-table-](/assets/img/Snipaste_2021-09-19_21-33-53.png)



## 总结：

如果还有有问题，思路时先排除是不是版本的问题，脑里时刻要有版本的意识， 这是小马哥说的，然后可以下载非min的js文件，然后报错的地方把断点，先看下报错的原因，再理解那附近代码及方法要起的作用，再找找整个实现原理，最后就是沉着气，一时半会解决不了，就先休息，后面就突然有思路了。