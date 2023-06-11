import os

# 激活名为scy的虚拟环境
import subprocess

os.system('conda activate scy')

a = ['scrapy',
     'crawl',
     'new_run1',
     '-a',
     'arg1=1',
     '-a',
     'arg2=12',
     '-a',
     'arg3=002878']
# 设置环境变量
env = os.environ.copy()
env['PYTHONPATH'] = ''
os.environ['SCRAPY_SETTINGS_MODULE'] = 'first_time.settings'
subprocess.run(a, cwd='local1',
               env={'PATH': 'C:\\Users\\11498\\miniconda3\\envs\\scy\\Scripts;'})
