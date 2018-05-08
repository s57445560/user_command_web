#!/usr/bin/python
# coding=utf8
# author: Sun yang
from fabric.api import *
import data_init


class Fabric_run(object):
    def __init__(self, command=False, user_passwd=False):
        self.command = command
        # 数据类型 [ user, passwd ]
        self.user_passwd = user_passwd
        ip_list, ip_dic = data_init.run()
        env.warn_only = True
        env.hosts = ip_list
        env.user = 'root'
        env.passwords = ip_dic

    def run_command(self):
        with settings(abort_on_prompts=True):
            try:
                with hide('running', 'stdout', 'stderr'):
                    return run(self.command)
            except:
                return "Failure to execute"

    # 第一次上报数据
    def check_host(self):
        with settings(abort_on_prompts=True):
            try:
                with hide('running', 'stdout', 'stderr'):
                    disk_k = run("fdisk -l 2>/dev/null|grep 'Disk /dev/s' 2>/dev/null|awk '{a+=$3}END{print a}'")
                    disk_num = run("fdisk -l 2>/dev/null|grep 'Disk /dev/s' 2>/dev/null|wc -l")
                    mem = run("free -g|awk 'NR==2{print $2}'")
                    cpu_num = run('cat /proc/cpuinfo |grep "processor"|wc -l')
                    cpu_model = run("cat /proc/cpuinfo | grep name | cut -f2 -d: | uniq -c|grep -Po '(?<=[0-9]).*' ")
                    v_s = run("lspci | grep -i vga|grep VMware >/dev/null&&echo '虚拟机'||echo '物理机'")
                    return "{disk_k}||{disk_num}||{mem}||{cpu_num}||{cpu_model}||{v_s}".format(disk_k=disk_k,
                                                                                               disk_num=disk_num,
                                                                                               mem=mem, cpu_num=cpu_num,
                                                                                               cpu_model=cpu_model,
                                                                                               v_s=v_s)
            except:
                return ""

    # 密码修改
    def mychange(self):
        result = run('echo "{passwd}" | sudo passwd {username} --stdin  >/dev/null&&echo "ok"||echo "error"'.format(
            username=self.user_passwd[0], passwd=self.user_passwd[1]))
        return result

    # 删除账号
    def mydel(self):
        if self.user_passwd[0].strip() == "root":
            return "error root not del"
        with settings(abort_on_prompts=True):
            try:
                with hide('running', 'stdout', 'stderr'):
                    result = run(
                        'userdel -r {username} 2>/dev/null&&echo "ok"||echo "error {username} no exist"'.format(
                            username=self.user_passwd[0]))
                    run("sed -i 's/^{username} .*//g' /etc/sudoers".format(username=self.user_passwd[0]))
                    return result
            except:
                return "Failure to execute"

    # 账号添加与禁用
    def myadd(self):
        if self.user_passwd[0].strip() == "root":
            return "error root not add or nologin"
        with settings(abort_on_prompts=True):
            try:
                with hide('running', 'stdout', 'stderr'):
                    result = run('useradd {username} 2>/dev/null||echo "error"'.format(username=self.user_passwd[0]))
                    if result == "error":
                        if self.user_passwd[2] == False:
                            run("usermod -L {username}".format(username=self.user_passwd[0]))
                            return "ok"
                        elif self.user_passwd[2] == True:
                            run("usermod -U {username}".format(username=self.user_passwd[0]))
                            return "ok"
                        return "error %s user exist" % self.user_passwd[0]
                    run('echo "{passwd}" | sudo passwd {username} --stdin  >/dev/null'.format(
                        username=self.user_passwd[0], passwd=self.user_passwd[1]))
                    run('echo "{username} ALL=(ALL) NOPASSWD: ALL" >>/etc/sudoers'.format(username=self.user_passwd[0]))
                    return "ok"
            except:
                return "Failure to execute"

    def running(self, obj, hosts=False):
        if hosts:
            return execute(obj, hosts=hosts)
        else:
            return execute(obj)
