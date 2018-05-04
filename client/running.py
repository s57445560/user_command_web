#!/usr/bin/python
# coding=utf8
import os
# 获取上一层模块路径并且添加到python环境变量中
BASE = os.path.dirname(os.path.abspath(__file__))+"/src"
print(BASE)
import sys
sys.path.append(BASE)
import settings
from src import post_get_method
from src import run_fabric
from src import main
from src.print_log import print_logs

def go():
    print_logs.info("-----------------------------------------------")
    print_logs.info("服务已开始启动")
    # 刚启动时获取所有任务id
    id_list = post_get_method.first_running()
    print_logs.info("已获取所有任务id")
    # 启动时检查管理主机的状态
    obj = run_fabric.Fabric_run()
    result = obj.running(obj.check_host)
    print_logs.info("所有主机状态已检查完毕,: %s" % result)
    for ip,data in result.items():
        if data == "":
            print_logs.error("主机检查失败: {ip}".format(ip=ip))
    # 把检查的状态发送给服务器
    result["name"] = settings.QY_NAME
    post = post_get_method.Send_Data()
    post_result = post.post_data(result,"/monitor/Get_taskid_all/")
    print_logs.info("主机状态已发送到服务端,: %s"% post_result)
    print(post_result)
    main_obj = main.Monitor(id_list)
    print_logs.info("服务已初始化!")
    main_obj.running()