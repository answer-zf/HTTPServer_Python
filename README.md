## HTTPSEVER 项目

### 核心功能点

-   httpserver 与 应用分离
-   用户配置文件确定软件功能
-   WebFrame 模拟后段框架 处理请求

### 核心技术点

-   httpserver 需要与两端建通信
-   WebFrame 采用 IO多路复用 的通信方式进行通信
-   数据传递采用 Json

###  项目结构

```

           | -- httpserver -- HttpServer.py (主程序)
           |               -- config.py(httpserver配置文件)
project -- |
           |
           |
           | -- WebFrame   -- WebFrame.py (主程序)
                           -- static (静态网页)
                           -- views.py (应用处理)
                           -- urls.py (路由配置)
                           -- settings.py (框架配置)
```

### http通信协议

-   httpserver -> webframe   {method:'GET',info:'/'}
-   webframe   -> httpserver {status:'200',data:'...'}