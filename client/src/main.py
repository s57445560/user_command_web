#!/usr/bin/python
# coding=utf8
# author: Sun yang
import sys, time
import post_get_method
import run_fabric
sys.path.append("../")
import settings
import print_log

class Monitor(object):
    def __init__(self,id_list):
        self.id_list = id_list
        self.interval = settings.INTERVAL
        self.qy_name = settings.QY_NAME
        self.api_obj = post_get_method.Send_Data()
        self.last_time = time.time()

    def task_handle(self, task_dic):
        hosts = task_dic.get("hosts")
        cmd = task_dic.get("cmd")
        # 如果是True 那么就是和账号相关的操作
        if task_dic.get("status_user"):
            user = task_dic.get("user")
            passwd = task_dic.get("passwd")
            login = task_dic.get("login")
            sudo = task_dic.get("sudo")
            fabric_obj = run_fabric.Fabric_run(user_passwd=[user, passwd, login,sudo])
            # 判断是否有此方法，如果没有则是非法指令
            if hasattr(fabric_obj,cmd):
                return fabric_obj.running(getattr(fabric_obj,cmd),hosts)
            print_log.print_logs.error("没找到此方法为非法指令: {cmd}".format(cmd=cmd))
            print(u"没找到此方法为非法指令")
            return False
        else:
            fabric_obj = run_fabric.Fabric_run(cmd)
            if not hosts:
                hosts = False
            print(hosts)
            return fabric_obj.running(fabric_obj.run_command,hosts)

    def change_file(self,user_passwd,post_json):
        if user_passwd[0].strip() == "root":
            with open('data/ip.conf',"r") as f:
                lines = f.readlines()
            with open('data/ip.conf', "w") as f_w:
                for line in lines:
                    if len(line.split()) != 0:
                        ip = line.split()[0]
                        if ip in post_json:
                            print(ip)
                            print(post_json)
                            if post_json[ip] == "ok":
                                f_w.write("%s %s\n"%(ip,user_passwd[1]))
                            else:
                                f_w.write(line)
                        else:
                            f_w.write(line)
    def report_time(self,now_time):
        if now_time - self.last_time >= settings.REPORT_TIME:
            self.last_time = now_time
            print_log.print_logs.info("客户端状态时间上报")
            print("client status report")
            post_result = self.api_obj.post_data({"name":self.qy_name,"time":now_time}, "/monitor/Monitor_status/")

    def running(self):
        while True:
            print_log.print_logs.info("已经开始任务获取,心跳间隔为 %s."% self.interval)
            print(self.interval)
            # 客户端上报时间
            self.report_time(time.time())
            # 返回的是 [{...},{...}] 最近发出的任务队列
            result = self.api_obj.get_data({},"/monitor/Get_put_task/")
            if result:
                # 循环任务队列
                for i in result:
                    # 如果任务id不在自己的 id_list队列内则 开始执行下面任务
                    if i["id"] not in self.id_list:
                        if self.qy_name in i["groups"] or "ALL" in i["groups"]:
                            # 开始执行任务
                            print_log.print_logs.info("开始执行任务 : {cmd}".format(cmd=i["cmd"]))
                            post_json = self.task_handle(i)
                            print(post_json)
                            if post_json:
                                if i.get("status_user"):
                                    # 判断是否是root 如果是 则修改配置文件
                                    self.change_file([i["user"],i["passwd"]],post_json)
                                post_json["name"] = self.qy_name
                                post_json["id"] = i["id"]
                                post_result = self.api_obj.post_data(post_json,"/monitor/Get_put_task/")
                                print_log.print_logs.info("任务执行完毕 : {cmd}".format(cmd=i["cmd"]))
                            else:
                                print_log.print_logs.error("任务执行失败 : {cmd}".format(cmd=i["cmd"]))
                        # 把任务id加入 任务队列
                        self.id_list.append(i["id"])
            else:
                print_log.print_logs.info("暂时无任务，或者get失败")
            time.sleep(self.interval)