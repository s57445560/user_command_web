#! /usr/bin/python
# coding:utf-8
# author: sunyang
# api validate
from django.shortcuts import HttpResponse
from execute_task.print_log import print_logs
import json
import time
import hashlib
from django.conf import settings
APPID_LIST = {}

APPID = settings.APPID
DEL_ID = []

# 生成md5  现在时间 + appid客户端传递过来的
def md5(appid,new_time):
    m = hashlib.md5()
    m.update(bytes(appid + new_time,encoding='utf-8'))
    return m.hexdigest()


#验证主体函数
def auth_status(request):
    DEL_ID = []
    api_id = request.META.get('HTTP_APPID')
    group_name = request.GET.get("group_name")
    # 如果客户端传递过来的appid不是用|分开的就报错
    try:
        appid_md5, client_time = api_id.split('|')
    except:
        print_logs.error("%s 非法用户连接" % group_name)
        return False
    local_time = time.time()
    float_client_time = float(client_time)
    # 大于10秒的请求丢弃
    if local_time - 10 > float_client_time:
        print_logs.info("%s api 请求大于10秒 请求丢弃"%group_name)
        return False
      # 循环已有的列表，超过20秒的放到丢弃列表内
    for id in APPID_LIST.keys():
        if local_time - 20 > APPID_LIST[id]:
            DEL_ID.append(id)
    # 循环丢弃列表 并且删除这个值
    for id in DEL_ID:
        print_logs.info("%s api 请求超过20秒 删除"%group_name)
        del APPID_LIST[id]
        print('del---------------')
    # 如果这次访问的api_id在已访问的列表内，证明此id被截获
    if api_id in APPID_LIST:
        print_logs.error("%s api 请求已经存在列表内，请求拒绝！"%group_name)
        return False

     # 如果匹配成功则把api_id当键 时间当value存入
    local_md5 = md5(APPID, client_time)
    if appid_md5 == local_md5:
        APPID_LIST[api_id] = float_client_time
        print_logs.info("%s api 请求成功,可以建立连接"% group_name)
        return True
    else:
        print_logs.error("%s api 请求失败,无法建立连接" % group_name)
        return False

# 装饰器
def apiauth(func):
    def para(*args, **kwargs):
        # 获取验证函数的request
        request = args[1]
        result = auth_status(request)
        print('11111111111',APPID_LIST)
        print(result)
        if not result:
            return HttpResponse(json.dumps({'code':'1001','message':'auth fail'}))
        return func(*args, **kwargs)
    return para