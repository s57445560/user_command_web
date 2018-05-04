#!/usr/bin/python
# coding=utf8
# author: Sun yang

import post_get_method

def first_running():
    obj = post_get_method.Send_Data()
    obj.get_data({},"/monitor/Get_taskid_all/")


