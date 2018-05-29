#!/usr/bin/python
# coding=utf8
# author: Sun yang

from fabric.api import *
import os
import sys
import time
import logging
import socket
import re

list_user_ip = []
ip_dict = {}
host_dict = {}
web_list = []
check_dict = {}
web_ip = []
es_ip = []
es_id = 1
lvs_dic = {}
LVS_RS_IP = []
keep_ip = []
env.warn_only = True

# 读取ip.conf 文件 来设置env.hosts 和env.passwords
with open('data/ip.conf') as f:
    for line in f.readlines():
        if line.rstrip() == '':
            continue
        list_line = line.rstrip().split()
        ip = list_line[0]
        if len(list_line) == 3:
            host = list_line[2]
            host_dict[ip] = host
        passwd = list_line[1]
        check_dict[ip] = 0
        ip_dict['root@' + ip + ':22'] = passwd
        ssh_ip = 'root@' + ip
        list_user_ip.append(ssh_ip)

env.hosts = list_user_ip

env.user = 'root'
env.passwords = ip_dict


@task
def go():
    run("touch  /var/log/command.log")
    run("chmod 777 /var/log/command.log")
    put("data/profile","/tmp/profile")
    run("cat /tmp/profile >>/etc/profile")
    run("yum install pciutils* -y")
