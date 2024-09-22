## 爬取东方财富股吧的帖子，评论，以及展开子评论
### 东方财富股吧中每一条帖子的爬取难度较低
#### 如果只需要爬取帖子的内容
    则不需要实例化浏览器，只需要通过发送request和接受response，而后直接对response进行解析即可获得相关数据。
#### 如果需要爬取帖子中的评论，以及对于评论的评论（子评论），展开子评论（子评论较多时需要点击展开按钮），以及评论的翻页，评论较多时会有多页评论。
    则需要实例化浏览器，这样才能接收到相关评论信息，同时实现自动点击展开按钮和评论翻页按钮。并最终将其封装到一个CLASS中，以一个Record的方式写入数据库中

### 环境配置 
    缺哪个就pip吧，请务必使用单独的虚拟环境
### 程序运行    
 * 主要修改位置，spider文件下的total.py

 * 直接隐藏类别total_page

  * 然后新建类别,这是一个示例，可以先往下看
    ```
    class Zazesus(total_page):
    name = '300612_1'

    def __init__(self, **kwargs):
        self.Stock_id = '688228'
        self.begin_page = 1
        self.end_page = 4
        self.tunnelhost = "k321.kdltps.com"
        self.tunnelport = "15818"
        self.proxy_username = "XXX"
        self.proxy_password = "XXXX"
        self.use_password = True  #不挂代理直接false就完事了
        self.use_ip = True #同上
        chrome_options = webdriver.ChromeOptions()
        if self.use_password:  # 用户名验证设置
            proxyauth_plugin_path = create_proxyauth_extension(
                self.tunnelhost,  # 隧道域名
                tunnelport=self.tunnelport,  # 端口号
                proxy_username=self.proxy_username,  # 用户名
                proxy_password=self.proxy_password)  # 密码
            chrome_options.add_extension(proxyauth_plugin_path)
        if self.use_ip:
            chrome_options.add_argument(f'--proxy-server=http://{self.tunnelhost}:{self.tunnelport}')

        prefs = {"profile.managed_default_content_settings.images": 2}  # 禁止加载图片
        chrome_options.add_experimental_option("prefs", prefs)
        self.header = {"Connection": "close"}
        self.driver = webdriver.Chrome(chrome_options=chrome_options)
    ```

爬虫前请修改股票代码，和起始页和终止页

若要采取一个页面中随机爬取帖子，请修改
```total_page```下的
```
if (current_url
                    # and (random.random() < 0.3)   #取消注释则一个页面随机爬取30%的帖子
            ):
```
这里被注释掉了，因为没有随机爬取，改变0.3的大小可以改变比例


### 爬虫运行
一个 这里是一个终端，一个类对应一个终端
```
class Zazesus(total_page):
    name = 'zaz_spider_name'
```
请务必自行修改class类的名称，但一定要继承total page

不要另外开一个py文件，就在total下面继续写！！！！！，因为我尝试重开一个发现继承不过去
### 自动化运行
运行启动命令为 scrapy crawl {your_spider_name}

在正确设置根目录的前提下，可以通过用python脚本启动多进程的方式对多个股票进行同时爬取。
### 文明爬取
但因为实例化浏览器的缘故，爬取过程中会被反爬程序封ip，因此建议使用代理，在代理使用过程中注意scrapy框架为异步爬取，因此对于一个进程来说，爬取过程中不要换ip,爬取速度稍微慢一点的情况下不会被封
    
### 数据存储和查看
数据自动存在mongodb中，一种非关系型数据库，可以直接导出json文件，方便读取

正常来说是自动存放在stock数据库中，然后对应股票代码的collection，这里建议先自行建立一个database

可以打开mongodb campass进行可视化查看,可以可视化建立数据库

### 测试建议
先设定两个false，即先不使用代理，直接爬看看能正常运行不

强行终止程序：狂按ctrl+c

    