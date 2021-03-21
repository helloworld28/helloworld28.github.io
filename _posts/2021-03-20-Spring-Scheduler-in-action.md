---
title: Spring scheduler 定时任务避坑使用指南及原理剖析
author: powerjun        
date: 2021-03-20 17:38:00 +0800
categories: [笔记,  技术杂记]
tags: [Spring,scheduler]
toc: true
---

## 前言

前面在公司里的应用，要有一个功能是需要同步另一个系统的数据到该系统缓存起来，而不是需要的时候才去取，所以就想到使用定时任务去定时去取数据，然后该应用是使用了 `SpringBoot` ,使用惯Spring 的同学都会想到，它会已经把你需要的功能已经集成 Spring 里了，这也正是Spring 的一大特点，集成主流的技术框架，让我们开箱即用，需求是简单的同步，就直接使用 `@EnableScheduling` `@Scheduled` 就可以实现定时任务。

但后面上线了一段时间后，发现定时任务停止了工作了，数据停止了更新，通过更新日志发现定时任务跑着跑着就停止了，然后因为应用是部署在 Docker 容器里，线程Dump 不出来，但通过日志分析到是最后一个定时任务并没有跑完，这就奇怪了，为什么上个任务没有执行完，就好像把整个定时任务功能给停止了，后面分析一遍 Spring scheduler 的源代码实现原理，问题终于变得十分通透。

## 简单使用

使用 SpringBoot 的应用并不需要添加其他的依赖，因为这个功能已经在  Spring 的核心包`spring-context`中了，所以可以直接开箱使用

1. 添加 `@EnableScheduling` 

   ```
   @SpringBootApplication
   @EnableScheduling
   public class SpringTaskApplication {
       public static void main(String[] args) throws InterruptedException {
           SpringApplication.run(SpringTaskApplication.class, args);
       }
   }
   ```

2. 在需要定时任务调用的方法上添加 `@Scheduled` 注解

   ```
   @Component
   public class SpringTasks {
       private static final Logger log = LoggerFactory.getLogger(SpringTasks.class);
       @Scheduled(fixedRate = 5000)
       public void reportCurrentTime(){
           log.info("The time is now {}", LocalDateTime.now());
       }
   }
   ```

更详细的使用指南可参考[官方的文档](https://spring.io/guides/gs/scheduling-tasks/)

## 原理分析

首先简单概括Spring Scheduler （Spring Scheduling Task） 的使用，就是在Java 原生`ScheduledExecutorService` 基础上作了简单的封装，把它里面的参数封装成了注解的参数，方便大家使用，同时也把定时任务，简间的类图依赖关系如下：

![](/assets/img/Spring-scheduler.png)

图上绿色部分为Spring的类，浅黄色的为Java 原生的类， 从图上可以简单地看到，先是注解的解析处理器`ScheduledAnnotationBeanPostProcessor` 它会拿到`@Scheduled` 注解的参数进行对应的处理如下：

```
protected void processScheduled(Scheduled scheduled, Method method, Object bean) {
		try {
			Runnable runnable = createRunnable(bean, method);
			boolean processedSchedule = false;
			String errorMessage =
					"Exactly one of the 'cron', 'fixedDelay(String)', or 'fixedRate(String)' attributes is required";

			Set<ScheduledTask> tasks = new LinkedHashSet<>(4);
			...
			// Check fixed rate
			long fixedRate = scheduled.fixedRate();
			if (fixedRate >= 0) {
				Assert.isTrue(!processedSchedule, errorMessage);
				processedSchedule = true;
				tasks.add(this.registrar.scheduleFixedRateTask(new FixedRateTask(runnable, fixedRate, initialDelay)));
			}
			...
	}
```

从代码里看到，就是取参数出来，封装到 `FixedRateTask` 类向下传递给 `ScheduledTaskRegistrar`，从这个类的名称能知道，它就是一下注册器，类似 Helper 类一样，辅助把定时任务注册到 `TaskScheduler`

org.springframework.scheduling.config.ScheduledTaskRegistrar#scheduleFixedRateTask(org.springframework.scheduling.config.FixedRateTask)

```
public ScheduledTask scheduleFixedRateTask(FixedRateTask task) {
		...
		if (this.taskScheduler != null) {
			if (task.getInitialDelay() > 0) {
				Date startTime = new Date(this.taskScheduler.getClock().millis() + task.getInitialDelay());
				scheduledTask.future =
						this.taskScheduler.scheduleAtFixedRate(task.getRunnable(), startTime, task.getInterval());
			}
			else {
				scheduledTask.future =
						this.taskScheduler.scheduleAtFixedRate(task.getRunnable(), task.getInterval());
			}
		}
		...
	}
```

从代码上看就是调用`TaskScheduler`它的其中一个实现类是`**ThreadPoolTaskScheduler**` 

org.springframework.scheduling.concurrent.ThreadPoolTaskScheduler#scheduleAtFixedRate(java.lang.Runnable, long)

```
public ScheduledFuture<?> scheduleAtFixedRate(Runnable task, long period) {
		ScheduledExecutorService executor = getScheduledExecutor();
		try {
			return executor.scheduleAtFixedRate(errorHandlingTask(task, true), 0, period, TimeUnit.MILLISECONDS);
		}
		catch (RejectedExecutionException ex) {
			throw new TaskRejectedException("Executor [" + executor + "] did not accept task: " + task, ex);
		}
	}
```

从代码里能看到最后就是从Task 里取出Runnable 传递给  `ScheduledExecutorService`这个类就是Java 原理的定时任务类型的线程池，所以目前从代码上来看，Spring 就是对 Java 原生定时任务线程池参数进行简单的封装。

### 定时任务线程池执行定时任务原理

定时任务线程池执行定时任务底层是使用 `DeplayQueue` +  ScheduledFutureTask 来实现的， 下面来分别来说下下这两个，先说DelayQueue

```
public class DelayQueue<E extends Delayed> extends AbstractQueue<E>
    implements BlockingQueue<E> {
	
    private final transient ReentrantLock lock = new ReentrantLock();
    
    //这是个权重队列，以时间数值来排序，越少越在前面，所以取出第一个肯定是最早要处理的任务
    private final PriorityQueue<E> q = new PriorityQueue<E>();
    
    ...
    
public E poll(long timeout, TimeUnit unit) throws InterruptedException {
        long nanos = unit.toNanos(timeout);
        final ReentrantLock lock = this.lock;
        lock.lockInterruptibly();
        try {
            for (;;) {
            	//取第一个元素出来
                E first = q.peek();
                if (first == null) {
                    if (nanos <= 0)
                        return null;
                    else
                        nanos = available.awaitNanos(nanos);
                } else {
                 	//判断这个元素是否已经到时间
                    long delay = first.getDelay(NANOSECONDS);
                    if (delay <= 0)
                        return q.poll();
                    if (nanos <= 0)
                        return null;
                    first = null; // don't retain ref while waiting
                    //下面为了等一定时间再来判断
                    if (nanos < delay || leader != null)
                        nanos = available.awaitNanos(nanos);
                    else {
                        Thread thisThread = Thread.currentThread();
                        leader = thisThread;
                        try {
                            long timeLeft = available.awaitNanos(delay);
                            nanos -= delay - timeLeft;
                        } finally {
                            if (leader == thisThread)
                                leader = null;
                        }
                    }
                }
            }
        } finally {
            if (leader == null && q.peek() != null)
                available.signal();
            lock.unlock();
        }
    }
    ...
  }
```



java.util.concurrent.ScheduledThreadPoolExecutor.ScheduledFutureTask

```
 private class ScheduledFutureTask<V>
            extends FutureTask<V> implements RunnableScheduledFuture<V> {

        /** The time the task is enabled to execute in nanoTime units */
        private long time;
        private final long period;

        /** The actual task to be re-enqueued by reExecutePeriodic */
        RunnableScheduledFuture<V> outerTask = this;
	
		...

        public boolean isPeriodic() {
            return period != 0;
        }

        private void setNextRunTime() {
            long p = period;
            if (p > 0)
                time += p;
            else
                time = triggerTime(-p);
        }
        /**
         * Overrides FutureTask version so as to reset/requeue if periodic.
         */
        public void run() {
            boolean periodic = isPeriodic();
            if (!canRunInCurrentRunState(periodic))
                cancel(false);
            else if (!periodic)
                ScheduledFutureTask.super.run();
            else if (ScheduledFutureTask.super.runAndReset()) {
            	//当任务执行完成后如果该重新计算下次执行的时间
                setNextRunTime();
                //重新把这个任务放回到DelayQueue
                reExecutePeriodic(outerTask);
            }
        }
    }
```

从这个类能看这个 `ScheduledFutureTask`类里有执行时间，是否周期任务，任务，在执行Run方法里就会根据是否为周期任务，把任务得新计算下次执行的时间，然后把任务放回到任务队列，然后线程池里的工作线程，就会从`DelayQueue` 里拿任务，所以能重新执行任务，所以在从这里能找到我们问题的答案了, **如果这个任务是没执行完那么就不会走到重新计算下次任务时间及把任务放到任务队列步骤。所以定时任务就不工作了 **

可以简单验证这个理论

```
public class SchedulerTest {

    @Test
    public void test() throws InterruptedException {
        ScheduledExecutorService scheduledExecutorService = Executors.newSingleThreadScheduledExecutor();
        scheduledExecutorService.scheduleAtFixedRate(()->{
            System.out.println("this is Now -> " + LocalDateTime.now());
            try {
                TimeUnit.SECONDS.sleep(5);
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
        }, 1, 1, TimeUnit.SECONDS);

        scheduledExecutorService.awaitTermination(1, TimeUnit.DAYS);
    }
```

设置了一秒走一次定时任务的，结果是5 秒一次

```
this is Now -> 2021-03-21T22:21:26.335
this is Now -> 2021-03-21T22:21:31.336
this is Now -> 2021-03-21T22:21:36.336
this is Now -> 2021-03-21T22:21:41.337
this is Now -> 2021-03-21T22:21:46.347
this is Now -> 2021-03-21T22:22:36.369
```

## 总结

总的来说，Spring scheduler 就是在Java 原生定时任务基础上作简单的封装，更容易使用，同时也提供对任务监控支持，这让我们容易使用，但要对这个原理有所理解，然后在实现定时任务逻辑时，要考虑到阻塞问题，如果定时任务耗时过长，可考虑异步执行，

顺便提一下我们遇到问题，本来的定时任务执行耗时正常是很快的，但在使用 gRPC 框架是没有使用到 DeadLine 参数，可能因为网络丢包情况，导致请求结果未响应，然后 gRPC 请求会一直阻塞，所以使用gRPC 的同学一定要注意了。

