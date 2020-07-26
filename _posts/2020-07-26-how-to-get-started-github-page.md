---
title: 怎样在Github Pages写博客
author: 庄稼
date: 2020-07-26 14:34:00 +0800
categories: [post, note]
tags: [Github Pages,Jekyll]
toc: true
---

# 怎样在Github Pages上写博客

## 初衷

我们可以用Github来build great things ，用Github Pages 来分享great things,我们可以用GitHub来写自己的博客，写这样的博客，我们可以有很多控制这个博客的所有的一切，同时不要担心数据库存储的问题，让我们可专注于内容，我就是因为这样才喜欢上了Github Pages了，愿意花一周的时间来折腾它，为了让新手入门少走弯路，特此写一下我所走的弯路，以此警示后来之人。

## 工具准备

* your-name.github.io, 这样的仓库
* 本地电脑安装 git 
* jekyll
* Markdown编辑工具，如Typora (我喜欢）

关于创建像your-name.github.io, 这样仓库的操作步骤很简单，作为程序员的基本操作，可以参考以下链接

[官方指南](https://pages.github.com/)

安装 git 与Markdown,可以直接在软件管家直接安装即可, 在些着重介绍一下jekyll，这软件是作为把文本生成网页开源软件，让我们可以直接编辑markdown文件，Jekyll可以把它渲染到网页，有点像freemaker这样框架，只是它更多功能更好用，本地可以安装也可以不用装，安装了它就可以在本地直接生成网页，然后在本地直接预览，如果没有安装它也是可以的，只是写的博客没有预览的功能，把文章push到github上后，将会由github来生成网页。

有一点比较坑的就是，这个Jekyll官方是不支持Windows平台的，作为使用Windows 10的用户，它官网推荐使用Windows 10 的子系统来安装它，然后我就根据它的意思尝试使用win10 下的Linux 子系统来安装它，或者尝试使用docker来安装它，Jekyll依赖Ruby，然后这个Linux子系统正常的Linux发行片一样的正常，估计精简了很核心功能，然后Jekyll依赖Ruby一堆的，安装是就提示这个没有，那没有的，缺胳膊少腿的，安装不成功，好折腾，建议不要想着用Linux子系统来安装它了或者Docker来安装，有点得不偿失，建议使用官网推荐的另一个方法在windows上通过RubyInstall直接安装Ruby,然后按照教程安装Jekyll

 [Jekyll安装](https://jekyllrb.com/docs/installation/windows/)

##  博客主题选择

在决定写博客的时候，其中很重要的一件事情，就是选择自己喜欢的主题博客，如果你是前端大神，想拥有独一无二的博客外观，完全可以参考某一成熟的主题来自研样式主题，一般人都不想花太多时间在前端，就可以直接去Jeykyll 主题网站去在千万个主题选个你喜欢的Style，就好像在千万个人中，你终于遇上的对的她/他，以下就是主题网站：

You can find and preview themes on different galleries:

- [jamstackthemes.dev](https://jamstackthemes.dev/ssg/jekyll/)
- [jekyllthemes.org](http://jekyllthemes.org/)
- [jekyllthemes.io](https://jekyllthemes.io/)
- [jekyll-themes.com](https://jekyll-themes.com/)

里面的主题都会有github的仓库地址，就可以fork到自己的仓库里，然后主题都会有个简单的使用教程的，一般都是能过改配置文件，_config.yml文件，改完就可以了，我会把所有文件拷到个人的博客的仓库如“helloworld28.github.io”这个仓库把它push到master分支

##  使用实践

按照指南安装完成后，常用的指令就有以下三个

1. 在存在GemFile文件的目录下执行

   ~~~
   bundle install
   ~~~

   这个命令就像Maven的Install  一样解析依赖，下载依赖到本地

2. 利用jekyll生成文件

   ~~~
   bundle exec jekyll build
   ~~~

   执行这个命令，就要在目录里生成_site文件夹，里面会存放网站所有的页面文件及资源文件，可以直接把这个目录下的文件直接拿去部署

3. 启用本地的预览

   ~~~
   bundle exec jekyll serve
   ~~~

   执行完这个指令后可以看到提示，会监听4000端口，就是通过http://localhost:4000去预览生成的网站

## 写博客

当上面的事情都弄完，写博客就是很简单轻松的事情，就只需要用markdown写文档，写完push上去就可以通过看博客地址看到刚写的博客了，跟CSDN或者cnblog没有区别，就是感觉专注内容，而且用专业的Markdown去写感觉特别的顺手，让写博客变成一件愉快的事情。以下就是我的写博客截图，简单明了

![我的写博客工作界面](/assets/img/image-20200726202146839.png)

