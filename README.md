# 优化热榜类RSS feed源

自己个人很喜欢用传统的RSS feed源来获取信息，因为其简洁纯净的风格，可以避免App推荐算法带来的信息茧房，以及广告与用户评论带来的嘈杂；RSS的集成性，使只用一个完全定制的app接受各种信息变为可能，提供很不错的浏览体验。但有一类比较重要的信息与RSS适配不算完美，就是各大平台的热榜（例如，微博热搜、知乎热榜等），这些热榜类信息代表时下社会热点。

现有的热榜类RSS feed源，以[RssHub](https://docs.rsshub.app/)为例，不能带来很好的浏览体验，其原因有三：首先，热榜channel是以每一条热榜条目为item，每条item在channel出现的顺序并非按照热度顺序呈现，很难定位到头部重点热点内容；二是以热榜条目为item，整个channel内会出现一段时间内所有的热榜条目，数量庞大；三是传统意义上，RSS item应该以一篇文章为单位，热榜中每条条目单独作为一条item，信息量极小，与RSS阅读器的操作逻辑不符合。

于是，我自己搭建了一个为热榜类信息优化的RSS源，本文记录一下相关细节。

<!--more-->

![左图：优化后的热榜RSS Feed；右图优化前的微博热榜RSS Feed](https://s1.ax1x.com/2022/04/09/LiKCfH.png)

## Feed优化

优化后的RSS feed 将多个网站平台的热榜集成到一个channel，每个单独平台的热榜作为单独的一个item，item里面的内容会将热榜的条目按热榜本身的顺序呈现。RSS feed会每一段时间（例如15分钟）更新一次，抓取各个平台的热榜榜单。更新后的榜单，不会以新item的方式加入channel，而是覆盖掉原来对应的item，例如20点15分的微博热搜item，会覆盖掉20点的微博热搜item。

这样优化后，热榜榜单条目以item文章形式展示，保留原榜单顺序；channel内item数量不会增加，固定为热榜平台来源的数量；item内容的信息不再只是热榜条目一行，而是整个榜单，信息密度增加，符合RSS阅读器的操作逻辑；除了解决传统热榜RSS feed源的三个问题外，优化后的Feed还保证了阅读器所浏览的热榜信息的时效性。

## 更多实现的细节

整个Feed源的实现其实很简单，通过Python脚本爬取[今日热榜](https://tophub.today/)中的条目，再通过模版化渲染输出xml，定时推送的到网页服务器上。其中，我们可以利用Github Action，设置cron定时任务，进行热榜信息抓取，并将输出的xml文本commit到Github page上，采用公开的public repo完成这套流程是免费的，不产生任何花销。

但这种方案有些许不足。在部署上，因为热榜时效性上的要求，定时任务频率很高，每隔10分钟更新一次，就会产生一次commit，一天下来会有很多commit，可能会对自己Github contribution产生一定影响。另外，国内网络访问Github可能会出现延迟过高的问题。针对这两点，我最后选择将xml文本挂在[Vercel](https://vercel.com/)上，国内网络访问不会出现问题，对于静态网站，网页挂载也是免费的。

此外，今日热榜网站还会有反爬的限制，数据抓取时候qps不能太高。今日热榜的热榜条目链接，采用了网站内部转链的方式，后期访问如果没有今日热榜主站的session，直接访问转链并不能直接跳转，所以在进行链接爬取时候，不能直接爬下热榜条目url，还需要二次访问来获得源url。如果用request进行http请求发送，后面直接访问`.url`属性即可得到源url。

## demo

现在项目的代码参见[https://github.com/FarseaSH/trending-topics-rss](https://github.com/FarseaSH/trending-topics-rss)，后期我会将接口设计，在fork该repo后，通过简单修改，就能把自己想要看到的若干热榜集成在一起，生成自己定制的RSS热榜feed源。

现在项目demo的RSS feed地址为[trending-topics-rss.vercel.app](http://trending-topics-rss.vercel.app/)。