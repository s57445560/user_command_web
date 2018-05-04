#!/usr/bin/python
from django.shortcuts import render,HttpResponse
import json

def check(objects,dic):
    objs = objects.filter(dic)
    if objs:
        return False
    return True


def check_form(method, model, check_dic,not_edit_field=False):
    message = ""
    for dic in check_dic:
        if not_edit_field:
            if dic["field"] in not_edit_field :
                continue
        method_field = method.get(dic["field"],"")
        data_dic = {dic["field"]:method_field}
        print(data_dic)
        print(len(''.join(list(data_dic.values())[0])))
        if not dic["null"]:
            print(None in data_dic.values())
            if "" in data_dic.values():
                print("走了")
                message = "%s 项目不能为空!" % dic["name"]
                return message

        if len(''.join(list(data_dic.values())[0])) < dic["min_len"]:
            print(len(''.join(list(data_dic.values())[0])),"aaa")
            message = "%s 长度不能小于%s!" % (dic["name"],dic["min_len"])
            return message

        if dic["unique"]:
            objs = model.objects.filter(**data_dic)
            if objs:
                message = "%s 已存在!" % dic["name"]
                return message
    return message
