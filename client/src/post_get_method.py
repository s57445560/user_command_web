#!/usr/bin/python
# coding=utf8
# author: Sun yang
import requests
import sys
import time, hashlib
sys.path.append("../")
import settings
import print_log


class Send_Data(object):
    def __init__(self):
        self.number = 1
        # data, client_time = self.md5(settings.APPID)
        # new_appid = 'a94ff928a82749d017a873902922e650|1501150616.916467'
        # self.new_appid = "%s|%s" % (data, client_time)

    def init_api(self):
        data, client_time = self.md5(settings.APPID)
        self.new_appid = "%s|%s" % (data, client_time)

    def md5(self,appid):
        new_time = str(time.time())
        m = hashlib.md5()
        m.update(bytes(appid + new_time))
        return m.hexdigest(),new_time

    def post_data(self,data_dict,uri):
        self.init_api()
        """失败时会重试N次"""
        result_json = False
        if self.number <= settings.POST_RETRY:
            try:
                result = requests.post(url='%s%s' % (settings.URL,uri),
                                  data=data_dict, headers={'appid': self.new_appid},timeout=10)

                result_json = result.json()
                if result_json.get('code') == '1001':
                    self.number += 1
                    print_log.print_logs.error("与服务器端的鉴权失败.")
                    time.sleep(settings.POST_RETRY_TIME)
                    self.post_data(data_dict,uri)
            except Exception as a:
                print("fail %s" % self.number)
                print_log.print_logs.error("POST 请求失败 %s" % a)
                self.number += 1
                time.sleep(settings.POST_RETRY_TIME)
                self.post_data(data_dict,uri)
        self.number = 0
        return result_json

    def get_data(self,data_dict,uri):
        self.init_api()
        """失败时会重试N次"""
        result_json = False
        if self.number <= settings.GET_RETRY:
            try:
                result = requests.get(url='%s%s' % (settings.URL,uri),
                                params=data_dict ,timeout=10)
                result_json = result.json()
            except Exception as a:
                print("fail %s" % self.number)
                print_log.print_logs.error("GET 请求失败 %s" % a)
                self.number += 1
                time.sleep(settings.GET_RETRY_TIME)
                self.get_data(data_dict,uri)
        self.number = 0
        return result_json


def first_running():
    obj = Send_Data()
    return obj.get_data({},"/monitor/Get_taskid_all/")
