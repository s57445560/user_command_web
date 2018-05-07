from django.shortcuts import render, HttpResponse, redirect
from django.utils import timezone
# Create your views here.
from django.views import View
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from task.check_data import check, check_form
from task.forms import UserForm
from task import models
from task import my_form
import json, datetime, re, time
from task import auth
from execute_task.print_log import print_logs
from django.conf import settings
from django.db.models import Count, Min, Max, Sum
from task import permission


# 登陆装饰器
def login_auth(func):
    def inner(self, request, *args, **kwargs):
        user = request.session.get('user', None)
        if not user:
            return redirect('/monitor/login/')
        return func(self, request, *args, **kwargs)

    return inner


# 登陆页面
class Login(View):
    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        print('before')
        result = super(Login, self).dispatch(request, *args, **kwargs)
        print('after')
        return result

    def get(self, request):
        return render(request, "login.html")

    def post(self, request):
        username = request.POST.get("username")
        password = request.POST.get("password")
        obj = models.UserInfo.objects.filter(user=username, passwd=password)
        if obj:
            message = ""
            request.session["user"] = username
        else:
            message = "密码错误请回忆."
        return HttpResponse(json.dumps({"message": message}))


# 登出页面
def Logout(request):
    del request.session["user"]
    return redirect("/monitor/login/")


# api   客户端启动第一次获取所有的task id
class Get_taskid_all(View):
    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        print('before')
        result = super(Get_taskid_all, self).dispatch(request, *args, **kwargs)
        print('after')
        return result

    def get(self, request):
        task_dict = []
        print_logs.info("%s 获取任务id" % request.META['REMOTE_ADDR'])
        objs = models.Task.objects.all().values("id")
        for obj in objs:
            print(obj)
            task_dict.append(obj["id"])
        return HttpResponse(json.dumps(task_dict))

    @auth.apiauth
    def post(self, request):
        name = request.POST.get("name")
        group_obj = models.Groups.objects.filter(name=name).first()
        if group_obj:
            for ip in request.POST:
                if ip == "name":
                    continue
                if request.POST.get(ip) != "":
                    host_dic = {}
                    host_info = request.POST.get(ip)
                    host_info_list = host_info.split("||")
                    print(ip, host_info_list)
                    host_dic["disk_capacity"] = host_info_list[0] + "G"
                    host_dic["disk_num"] = host_info_list[1]
                    host_dic["memory"] = host_info_list[2] + "G"
                    host_dic["cpu"] = host_info_list[3]
                    host_dic["cpu_model"] = host_info_list[4]
                    host_dic["v_or_s"] = host_info_list[5]
                    print_logs.info("%s : 成功上报主机 %s" % (name, ip))
                    host_obj = models.Hosts.objects.filter(ip=ip, group_id_id=group_obj.id)
                    if host_obj:
                        print("存在")
                        host_obj.update(**host_dic)
                    else:
                        print("创建")
                        models.Hosts.objects.create(ip=ip, group_id_id=group_obj.id, **host_dic)

        else:
            print_logs.error("%s 不在企业鉴权表内,无法添加数据" % name)

        return HttpResponse(json.dumps({"data": "ok"}))


# api   客户端上报状态时使用
class Monitor_status(View):
    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        print('before')
        result = super(Monitor_status, self).dispatch(request, *args, **kwargs)
        print('after')
        return result

    @auth.apiauth
    def post(self, request):
        group_name = request.POST.get("name")
        time = request.POST.get("time")
        obj = models.Groups.objects.filter(name=group_name)
        if obj:
            obj.update(time=time)
        print(group_name, time)
        return HttpResponse(json.dumps({"data": "ok"}))


# api  监控的任务获取
class Get_put_task(View):
    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        print('before')
        result = super(Get_put_task, self).dispatch(request, *args, **kwargs)
        print('after')
        return result

    def get(self, request):
        task_list = []
        task_dict = {}
        print(request.method)
        task_objs = models.Task.objects.filter(time__gt=timezone.now() + datetime.timedelta(minutes=-180))
        # 生成api的数据格式 [{task...},{task...}]
        for task in task_objs:
            task_dict["groups"] = task.task_group.split(',')
            task_dict["cmd"] = task.cmd
            task_dict["status_user"] = task.status_user
            task_dict["login"] = task.login
            task_dict["user"] = task.user
            task_dict["passwd"] = task.passwd
            if task.hosts == None:
                task_dict["hosts"] = ""
            else:
                task_dict["hosts"] = task.hosts.split(',')
            task_dict["id"] = task.id
            task_list.append(task_dict)
            task_dict = {}
        return HttpResponse(json.dumps(task_list))

    @auth.apiauth
    def post(self, request):
        p = re.compile(r"Failure to execute|^error")
        # 任务执行完毕后会把结果发送到此处
        group_name = request.POST.get("name")
        print_logs.info("result data info: %s" % request.POST)
        id = request.POST.get("id")
        for ip in request.POST:
            if ip not in ["name", "id"]:
                result_data = request.POST.get(ip)
                if p.findall(result_data):
                    # 执行失败的任务
                    models.Task_result.objects.create(task_id_id=id, group_name=group_name, task_status=False, ip=ip,
                                                      message=result_data)
                else:
                    # 执行成功的任务
                    models.Task_result.objects.create(task_id_id=id, group_name=group_name, task_status=True, ip=ip,
                                                      message=result_data)
        return HttpResponse(json.dumps({"status": True}))


# 主页面
class Index(View):
    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        print('before')
        result = super(Index, self).dispatch(request, *args, **kwargs)
        print('after')
        return result

    # 给主页返回需要数据
    @login_auth
    def get(self, request):
        for_list = []
        for_dic = {}
        if request.GET.get("status"):
            groups_obj = models.Groups.objects.all()
            for group in groups_obj:
                for_dic = {}
                print(group.time)
                group_name = group.name
                last_time = group.time
                for_dic["name"] = group_name
                if last_time:
                    # 时间转换
                    format_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(float(last_time)))
                    # 企业上报超时的处理方法
                    if time.time() - float(last_time) >= settings.M_TIMEOUT:
                        for_dic["status"] = False
                    else:
                        for_dic["status"] = True
                    for_dic["time"] = format_time
                else:
                    for_dic["time"] = "企业从未上传数据"
                    for_dic["status"] = False
                for_list.append(for_dic)
            host_num = models.Hosts.objects.aggregate(n=Count('id'))["n"]
            group_num = models.Groups.objects.aggregate(n=Count('id'))["n"]
            task_num = models.Task.objects.aggregate(n=Count('id'))["n"]
            user_num = models.User.objects.aggregate(n=Count('id'))["n"]
            return HttpResponse(json.dumps(
                {"data": for_list, "host_num": host_num, "group_num": group_num, "task_num": task_num,
                 "user_num": user_num}))
        if request.GET.get("getuser"):
            user = request.session.get("user")
            return HttpResponse(json.dumps({"user": user}))
        return render(request, "index.html")


# 命令执行页面
class Command(View):
    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        print('before')
        result = super(Command, self).dispatch(request, *args, **kwargs)
        print('after')
        return result

    @login_auth
    def get(self, request):
        # 获取数据时使用
        if request.GET.get("status") == "GET":
            data_list = []
            change_list = []
            pt_list = []
            user_list = models.User.objects.get_queryset().order_by('id').values("username", "name", "status")
            group_list = models.Groups.objects.get_queryset().order_by('id').values("id", "name")
            for user in user_list:
                if user["username"] == "root":
                    continue
                ls_dic = {}
                if user["status"] == "可用":
                    ls_dic["label"] = user["name"]
                    ls_dic["value"] = user["username"]
                    change_list.append(ls_dic)
                ls_dic["label"] = user["name"]
                ls_dic["value"] = user["username"]
                data_list.append(ls_dic)
            pt_list.append({"lable": "ALL", "value": "ALL"})
            for group in group_list:
                ls_dic = {}
                ls_dic["label"] = group["name"]
                ls_dic["value"] = group["name"]
                pt_list.append(ls_dic)

            return HttpResponse(json.dumps({"data": data_list, "pt": pt_list, "change_list": change_list}))
        # 获取主机列表时使用
        if request.GET.get("status") == "host_list":
            group = request.GET.get("group")
            if group:
                obj = models.Groups.objects.filter(name=group).first()
                print(obj.id)
                host_obj = models.Hosts.objects.filter(group_id_id=obj.id).values("id", "ip")
                host_list = []
                for ip in host_obj:
                    host_list.append(ip["ip"])
                print(host_list)
                return HttpResponse(json.dumps({"data": host_list}))
        return render(request, "command.html")

    @login_auth
    @permission.check_permission
    def post(self, request):
        re_status = "false"
        obj_dic = {}
        username = request.POST.get('value')
        status = request.POST.get('status')
        ipstr = request.POST.get("ipstr")
        pt = request.POST.get('pt')
        # 执行命令
        if status == "cmd":
            if ipstr == "":
                models.Task.objects.create(cmd=username, task_group=pt)
            else:
                models.Task.objects.create(cmd=username, hosts=ipstr.strip(","), task_group=pt)
            print("laile11111")
            return HttpResponse(json.dumps({"data": "ok", "status": "true"}))
        pt_list = pt.split(",")
        obj = models.User.objects.filter(username=username).first()
        obj_dic["user"] = obj.username
        obj_dic["passwd"] = obj.passwd
        print(username, status, pt)
        # 添加账号
        if status == "myadd":
            print("myadd")
            if obj.status == "可用":
                obj_dic["login"] = True
            else:
                obj_dic["login"] = False
            if "ALL" in pt_list:
                models.Task.objects.create(task_group="ALL", cmd="myadd", status_user=True, **obj_dic)
            else:
                models.Task.objects.create(task_group=pt, cmd="myadd", status_user=True, **obj_dic)
            models.User.objects.filter(username=username).update(push_status="已推送")
            re_status = "true"
        # 删除账号
        if status == "mydel":
            if "ALL" in pt_list:
                models.Task.objects.create(task_group="ALL", cmd="mydel", status_user=True, **obj_dic)
            else:
                models.Task.objects.create(task_group=pt, cmd="mydel", status_user=True, **obj_dic)
            models.User.objects.filter(username=username).update(push_status="已推送")
            re_status = "true"

        # 修改账号
        if status == "mychange":
            if "ALL" in pt_list:
                models.Task.objects.create(task_group="ALL", cmd=status, status_user=True, **obj_dic)
            else:
                models.Task.objects.create(task_group=pt, cmd=status, status_user=True, **obj_dic)
            models.User.objects.filter(username=username).update(push_status="已推送")
            re_status = "true"
        return HttpResponse(json.dumps({"data": "aaaaa", "status": re_status}))


# 用户页面
class User(View):
    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        print('before')
        result = super(User, self).dispatch(request, *args, **kwargs)
        print('after')
        return result

    @login_auth
    def get(self, request):
        return render(request, "user.html")

    @login_auth
    def post(self, request):
        name = request.POST.get("name")
        username = request.POST.get("username")
        passwd = request.POST.get("passwd")
        status = request.POST.get("status")

        message = check_form(request.POST, models.User, my_form.USER)
        print(message)
        if message == "":
            print(status, "aacccc")
            if status == "true":
                models.User.objects.create(username=username, passwd=passwd, status="可用", name=name, push_status="未推送")
            else:
                models.User.objects.create(username=username, passwd=passwd, status="停用", name=name, push_status="未推送")
        return HttpResponse(json.dumps({"message": message}))


# 用户展示页面
class User_list(View):
    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        print('before')
        result = super(User_list, self).dispatch(request, *args, **kwargs)
        print('after')
        return result

    @login_auth
    def get(self, request):
        return render(request, "user_list.html")

    @login_auth
    def post(self, request):
        currentPage = request.POST.get('currentPage')
        handlesize = request.POST.get('handlesize')
        if currentPage and handlesize:
            objs = models.User.objects.get_queryset().order_by('id').values()
            total = int(len(objs))
            paginator = Paginator(objs, handlesize)  # 每页显示2个 并且把数据传入进来
            try:
                contacts = paginator.page(currentPage)  # 判断有没有page数值
            except PageNotAnInteger:
                # If page is not an integer, deliver first page.
                contacts = paginator.page(1)  # 如果没有设置page就返回第一页
            except EmptyPage:
                contacts = paginator.page(paginator.num_pages)  # 如果超过最大页 就返回最大页
            return HttpResponse(json.dumps({"total": total, "data": list(contacts)}))
        return render(request, "index.html")


# 用户编辑
class User_edit(View):
    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        print('before')
        result = super(User_edit, self).dispatch(request, *args, **kwargs)
        print('after')
        return result

    @login_auth
    def post(self, request):
        username = request.POST.get("username")
        passwd = request.POST.get("passwd")
        status = request.POST.get("status")
        push_status = request.POST.get("push_status")
        id = request.POST.get("id")
        dic = {'可用': "true", "停用": "false"}
        print(id, username, passwd, status,push_status)
        user_obj = models.User.objects.filter(id=id).first()
        # 如果都相等证明没有变化 直接返回。
        if user_obj.passwd == passwd and dic[user_obj.status] == status:
            return HttpResponse(json.dumps({"message": "", "status": user_obj.status, "passwd": passwd,"push_status": push_status}))
        message = check_form(request.POST, models.User, my_form.USER, not_edit_field=["username", "name"])
        print(message)
        if message == "":
            if status == "true":
                models.User.objects.filter(id=id).update(passwd=passwd, status="可用", push_status="未推送")
                status = "可用"
            else:
                models.User.objects.filter(id=id).update(passwd=passwd, status="停用", push_status="未推送")
                status = "停用"
        passwd = passwd
        return HttpResponse(json.dumps({"message": message, "status": status, "passwd": passwd, "push_status": "未推送"}))


# 用户删除
class User_del(View):
    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        print('before')
        result = super(User_del, self).dispatch(request, *args, **kwargs)
        print('after')
        return result

    @login_auth
    def post(self, request):
        id = request.POST.get("id")
        models.User.objects.filter(id=id).delete()
        return HttpResponse(json.dumps({"status": "ok"}))


# 主机显示页面
class Host_info(View):
    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        print('before')
        result = super(Host_info, self).dispatch(request, *args, **kwargs)
        print('after')
        return result

    @login_auth
    def get(self, request):
        return render(request, 'host.html')

    @login_auth
    def post(self, request):
        currentPage = request.POST.get('currentPage')
        handlesize = request.POST.get('handlesize')
        pt = request.POST.get('pt')
        pt_list = []
        print(pt)
        group_list = models.Groups.objects.get_queryset().order_by('id').values("id", "name")
        for group in group_list:
            ls_dic = {}
            ls_dic["label"] = group["name"]
            ls_dic["value"] = group["id"]
            pt_list.append(ls_dic)
        if currentPage and handlesize:
            if pt:
                host_objs = models.Hosts.objects.get_queryset().order_by('id').filter(group_id_id=pt).values('ip',
                                                                                                             'memory',
                                                                                                             'group_id__name',
                                                                                                             'v_or_s',
                                                                                                             'cpu',
                                                                                                             'cpu_model',
                                                                                                             'disk_capacity',
                                                                                                             'disk_num')
            else:
                host_objs = models.Hosts.objects.get_queryset().order_by('id').values('ip', 'memory', 'group_id__name',
                                                                                      'v_or_s', 'cpu', 'cpu_model',
                                                                                      'disk_capacity', 'disk_num')
            total = int(len(host_objs))
            paginator = Paginator(host_objs, handlesize)  # 每页显示2个 并且把数据传入进来
            try:
                contacts = paginator.page(currentPage)  # 判断有没有page数值
            except PageNotAnInteger:
                # If page is not an integer, deliver first page.
                contacts = paginator.page(1)  # 如果没有设置page就返回第一页
            except EmptyPage:
                contacts = paginator.page(paginator.num_pages)  # 如果超过最大页 就返回最大页
            return HttpResponse(json.dumps({"total": total, "data": list(contacts), "pt": pt_list}))

        return HttpResponse(json.dumps({"total": 0, "data": list([])}))


# 序列化时间格式
class DateEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(obj, date):
            return obj.strftime("%Y-%m-%d")
        else:
            return json.JSONEncoder.default(self, obj)


# 任务查看
class Task_info(View):
    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        print('before')
        result = super(Task_info, self).dispatch(request, *args, **kwargs)
        print('after')
        return result

    @login_auth
    def get(self, request):
        currentPage = request.GET.get('currentPage')
        handlesize = request.GET.get('handlesize')
        print(currentPage, handlesize)
        fromat_list = []
        if currentPage and handlesize:
            host_objs = models.Task.objects.get_queryset().order_by('-id').values('id', 'task_group', 'cmd',
                                                                                  'time', 'hosts', 'user', )
            total = int(len(host_objs))
            paginator = Paginator(host_objs, handlesize)  # 每页显示2个 并且把数据传入进来
            try:
                contacts = paginator.page(currentPage)  # 判断有没有page数值
            except PageNotAnInteger:
                # If page is not an integer, deliver first page.
                contacts = paginator.page(1)  # 如果没有设置page就返回第一页
            except EmptyPage:
                contacts = paginator.page(paginator.num_pages)  # 如果超过最大页 就返回最大页
            for dic in contacts:
                if dic["cmd"] == "myadd":
                    dic["cmd"] = "账号添加"
                    dic["color"] = "success"
                elif dic["cmd"] == "mychange":
                    dic["cmd"] = "账号变更"
                    dic["color"] = "success"
                elif dic["cmd"] == "mydel":
                    dic["cmd"] = "账号删除"
                    dic["color"] = "success"
                else:
                    dic["color"] = "primary"
                ok = 0
                err = 0
                all = 0
                for obj in models.Task_result.objects.filter(task_id_id=dic["id"]):
                    if obj.task_status:
                        ok += 1
                    else:
                        err += 1
                dic["ok"] = ok
                dic["err"] = err
                print(dic["hosts"])
                if dic["hosts"] == "" or dic["hosts"] == None:
                    if dic["task_group"] == "ALL":
                        print("aaaaaa")
                        all = len(models.Hosts.objects.all())
                    else:
                        print("bbbbb")
                        for group in dic["task_group"].split(","):
                            all += len(models.Hosts.objects.filter(group_id__name=group))
                else:
                    print("ccccc")
                    all = len(dic["hosts"].split(","))
                dic["all"] = all
                fromat_list.append(dic)
            return HttpResponse(json.dumps({"total": total, "data": fromat_list}, cls=DateEncoder))
        return render(request, 'task.html')

    @login_auth
    def post(self, request):
        task_id = request.POST.get("id")
        result_list = []
        if request.POST.get("status") == "GET_OK":
            obj = models.Task.objects.filter(id=task_id).first()
            if obj.task_group == "ALL":
                groups = models.Groups.objects.all()
                for group in groups:
                    result_idc = {}
                    result_idc["name"] = group.name
                    result_idc["list"] = []
                    task_objs = models.Task_result.objects.filter(group_name=group.name, task_id_id=task_id).all()
                    for task in task_objs:
                        task_dic = {}
                        task_dic[task.ip] = task.message
                        result_idc["list"].append(task_dic)
                    result_list.append(result_idc)
            else:
                if obj.hosts == "" or obj.hosts == None:
                    task_group_list = obj.task_group.split(",")
                    for group in task_group_list:
                        result_idc = {}
                        result_idc["name"] = group
                        result_idc["list"] = []
                        task_objs = models.Task_result.objects.filter(group_name=group, task_id_id=task_id).all()
                        for task in task_objs:
                            task_dic = {}
                            task_dic[task.ip] = task.message
                            result_idc["list"].append(task_dic)
                        result_list.append(result_idc)
                else:
                    result_idc = {}
                    result_idc["name"] = obj.task_group
                    result_idc["list"] = []
                    task_objs = models.Task_result.objects.filter(group_name=obj.task_group, task_id_id=task_id).all()
                    for task in task_objs:
                        task_dic = {}
                        task_dic[task.ip] = task.message
                        result_idc["list"].append(task_dic)
                    result_list.append(result_idc)
            print(result_list)
            return HttpResponse(json.dumps({"data": result_list}))

        if request.POST.get("status") == "GET_ERROR":
            group_objs = models.Task_result.objects.filter(task_id=task_id, task_status=False).values(
                "group_name").annotate(
                c=Count('group_name'))
            for group in group_objs:
                result_idc = {}
                result_idc["name"] = group["group_name"]
                result_idc["list"] = []
                task_objs = models.Task_result.objects.filter(group_name=group["group_name"], task_id_id=task_id,
                                                              task_status=False).all()
                for task in task_objs:
                    task_dic = {}
                    task_dic[task.ip] = task.message
                    result_idc["list"].append(task_dic)
                result_list.append(result_idc)
            print("aaaaaaaaaaaaa")
            return HttpResponse(json.dumps({"data": result_list}))
        return HttpResponse(json.dumps({"total": 0, "data": list([])}))
