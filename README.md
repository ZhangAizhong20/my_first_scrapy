# my_first_scrapy
my_first_scrapy for my competition,please do not use it as any commence before 2023-07-16


# ZAZ 折寿奉献，请勿外传，请暂时不要用于任何商业活动。

#### 建议使用pycharm, vscode不太聪明的样子

### 除了first_time这个是我自己的，其他的包缺哪个就pip吧，请务必使用单独的虚拟环境
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
        self.proxy_username = "t17941167792939"
        self.proxy_password = "790msm5i"
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

爬虫前请修改股票代码，和起始页和终止页面

若要采取一个页面中随机爬取帖子，请修改
```total_page```下的
```
if (current_url
                    # and (random.random() < 0.3)   #取消注释则一个页面随机爬取30%的帖子
            ):
```
这里被注释掉了，因为没有随机爬取，改变0.3的大小可以改变比例



### 部分报错
1.请保证电脑安装了chrome浏览器
2. 若total.py中导入报错，但其实没错,可能只是一些设定问题

### 爬虫运行
一个 这里是一个终端，一个类对应一个终端
```
class Zazesus(total_page):
    name = 'zaz_spider_name'
```
请务必自行修改class类的名称，但一定要继承total page
请务必遵循我的示例重写(好吧是我类的继承没学好，，)
```

         
```
b不要另外开一个py文件，就在total下面继续写！！！！！，因为我尝试重开一个发现继承不过去
###关于代理

使用快代理——隧道代理———按量计费———更换ip时间1分钟，最大请求数量差不多一秒6-8次就行，带宽3mb够用
！！！以上是针对一个终端的代理

###单个爬虫终端运行

文件名别随便改

在正确的环境和目录下，这里的目录应该是.\first_time\first_time



vscode中应该是在cmd中

pycharm是在local

cmd 和local都在两个软件下面的terminal

换路径 cd "your absolute path"(第一个first_time的路径)

```angular2html
scrapy crawl your_spider_name
```
可以多开几个终端，然后运行不同的spider_name,因为```__int__```的重写,可以支持更换不同的代理
    
### 数据存储和查看
数据自动存在mongodb中，一种非关系型数据库，可以直接导出json文件，方便读取

正常来说是自动存放在stock数据库中，然后对应股票代码的collection，这里建议先自行建立一个database

可以打开mongodb campass进行可视化查看,可以可视化建立数据库

### 测试建议
先设定两个false，直接爬看看能正常运行不

强行终止程序：狂按ctrl+c

### 最后一点
这个爬虫要了我半条命，最近没做别的事，光在写这个，若比赛结果不好，还望罗总包涵
    
