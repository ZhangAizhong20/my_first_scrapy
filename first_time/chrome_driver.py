import json

import requests
import scrapy
from selenium import webdriver
import string
import zipfile
import re
import time

from first_time.items import Subcomment


def create_proxyauth_extension(tunnelhost, tunnelport, proxy_username, proxy_password, scheme='http', plugin_path=None):
    """代理认证插件
    args:
        tunnelhost (str): 你的代理地址或者域名（str类型）
        tunnelport (int): 代理端口号（int类型）
        proxy_username (str):用户名（字符串）
        proxy_password (str): 密码 （字符串）
    kwargs:
        scheme (str): 代理方式 默认http
        plugin_path (str): 扩展的绝对路径
    return str -> plugin_path
    """

    if plugin_path is None:
        plugin_path = 'vimm_chrome_proxyauth_plugin.zip'

    manifest_json = """
    {
        "version": "1.0.0",
        "manifest_version": 2,
        "name": "Chrome Proxy",
        "permissions": [
            "proxy",
            "tabs",
            "unlimitedStorage",
            "storage",
            "<all_urls>",
            "webRequest",
            "webRequestBlocking"
        ],
        "background": {
            "scripts": ["background.js"]
        },
        "minimum_chrome_version":"22.0.0"
    }
    """

    background_js = string.Template(
        """
        var config = {
                mode: "fixed_servers",
                rules: {
                singleProxy: {
                    scheme: "${scheme}",
                    host: "${host}",
                    port: parseInt(${port})
                },
                bypassList: ["foobar.com"]
                }
            };
        chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});
        function callbackFn(details) {
            return {
                authCredentials: {
                    username: "${username}",
                    password: "${password}"
                }
            };
        }
        chrome.webRequest.onAuthRequired.addListener(
                    callbackFn,
                    {urls: ["<all_urls>"]},
                    ['blocking']
        );
        """
    ).substitute(
        host=tunnelhost,
        port=tunnelport,
        username=proxy_username,
        password=proxy_password,
        scheme=scheme,
    )
    with zipfile.ZipFile(plugin_path, 'w') as zp:
        zp.writestr("manifest.json", manifest_json)
        zp.writestr("background.js", background_js)
    return plugin_path


def extract_time(text):
    # 定义匹配时间信息的正则表达式
    regex = r"(\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2})"
    # 使用正则表达式匹配时间信息
    matches = re.findall(regex, text)
    # 如果没有匹配到时间信息，则返回空字符串
    if not matches:
        return None
    # 返回第一个匹配到的时间信息
    return matches[0]


def get_ip_from_api(secret_id, secret_key):
    # 设置API地址
    url = "https://auth.kdlapi.com/api/get_secret_token"
    '''
    POST https://auth.kdlapi.com/api/get_secret_token HTTP/1.1
    Content-Type: application/x-www-form-urlencoded

    secret_id=o1fjh1re9o28876h7c08&secret_key=jd1gzm6ant2u7pojhbtl0bam0xpzsm1c
    '''
    # 设置POST请求的参数
    data = {
        "secret_id": secret_id,
        "secret_key": secret_key,
    }

    # 发送POST请求
    response = requests.post(url, data=data)

    # 获取返回结果中的密钥令牌
    secret_token = json.loads(response.text).get("data", {}).get("secret_token")
    print(secret_token)
    # 设置获取IP的API地址
    url = "https://tps.kdlapi.com/api/changetpsip"

    # 设置GET请求的参数
    params = {
        "secret_id": secret_id,
        "signature": secret_token,
    }

    # 发送GET请求
    response = requests.get(url, params=params)
    return json.loads(response.text).get('code', {})


def process_sub_comment(subcomment:scrapy.Selector):
    subcom = Subcomment()
    subcom['subtext'] = subcomment.css(
        'div.row1 > span.l2_short_text::text').get()
    subcom['subauthor'] = subcomment.css(
        'div.row1 > span.replyer > a::text').get()
    subcom['sublikes'] = subcomment.css(
        'div.row2.clearfix > div > span.level2_rebtn.replylike.unlike > span::text').get()  # comment_all_content > div > div:nth-child(10) > div > div.level2_box > div.level2_list > div:nth-child(1) > div.row2.clearfix > div > span.level2_rebtn.replylike.unlike > span
    subcom['subauthor_location'] = subcomment.css(
        'div.row2.clearfix > span.reply_ip::text').get()
    subcom['subtime'] = subcomment.css('div.row2.clearfix > span.time.fl::text').get()
    return subcom
# import os
# import tempfile
# import shutil
# from zipfile import ZipFile


# def create_proxyauth_extension2(tunnelhost, tunnelport, proxy_username, proxy_password, scheme='http', crx_path=None):
#     """生成Chrome代理认证插件"""
#
#     if crx_path is None:
#         crx_path = 'vimm_chrome_proxyauth_plugin.crx'
#
#     def generate_key_pair():
#         """生成RSA公钥和私钥"""
#         key = RSA.generate(1024)
#         private_key = key.exportKey("DER")
#         public_key = key.publickey().exportKey("DER")
#         return private_key, public_key
#
#     def generate_zip_file(tempdir, public_key):
#         """生成zip压缩包"""
#         manifest = {
#             "name": "Chrome Proxy",
#             "version": "1.0.0",
#             "manifest_version": 2,
#             "background": {
#                 "scripts": ["background.js"]
#             },
#             "permissions": [
#                 "proxy",
#                 "tabs",
#                 "unlimitedStorage",
#                 "storage",
#                 "<all_urls>",
#                 "webRequest",
#                 "webRequestBlocking"
#             ],
#             "key": public_key.decode()
#         }
#         with open(os.path.join(tempdir, 'manifest.json'), 'w') as f:
#             f.write(str(manifest))
#         with open(os.path.join(tempdir, 'background.js'), 'w') as f:
#             f.write("""
#                     var config = {
#                         mode: "fixed_servers",
#                         rules: {
#                             singleProxy: {
#                                 scheme: "%s",
#                                 host: "%s",
#                                 port: %s
#                             },
#                             bypassList: ["foobar.com"]
#                         }
#                     };
#                     chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});
#                     function callbackFn(details) {
#                         return {
#                             authCredentials: {
#                                 username: "%s",
#                                 password: "%s"
#                             }
#                         };
#                     }
#                     chrome.webRequest.onAuthRequired.addListener(
#                                 callbackFn,
#                                 {urls: ["<all_urls>"]},
#                                 ['blocking']
#                     );
#                     """ % (scheme, tunnelhost, tunnelport, proxy_username, proxy_password))
#         with ZipFile(crx_path, 'w') as zp:
#             zp.write(os.path.join(tempdir, 'manifest.json'), 'manifest.json')
#             zp.write(os.path.join(tempdir, 'background.js'), 'background.js')
#             zp.write(public_key_path, 'key.pem')
#
#     # 创建临时文件夹
#     tempdir = tempfile.mkdtemp()
#
#     # 生成RSA公钥和私钥，并保存公钥
#     private_key, public_key = generate_key_pair()
#     public_key_path = os.path.join(tempdir, 'key.pem')
#     with open(public_key_path, 'wb') as f:
#         f.write(public_key)
#
#     # 生成zip压缩包，并删除临时文件
#     generate_zip_file(tempdir, public_key)
#     shutil.rmtree(tempdir)
#
#     return crx_path
