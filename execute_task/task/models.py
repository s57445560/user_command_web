from django.db import models
from django.utils import timezone
import time
# Create your models here.

class Groups(models.Model):
    name = models.CharField(max_length=64, unique=True,verbose_name="企业名称")
    time = models.CharField(max_length=64,null=True)

    def __str__(self):
        return self.name


class Hosts(models.Model):
    group_id = models.ForeignKey(to="Groups",on_delete=models.CASCADE,verbose_name="主机id")
    ip = models.CharField(max_length=32,verbose_name="主机ip")
    disk_num = models.CharField(max_length=32,verbose_name="磁盘数量")
    disk_capacity = models.CharField(max_length=32,null=True,verbose_name="磁盘总大小")
    memory = models.CharField(max_length=32,verbose_name="内存大小")
    cpu_model = models.CharField(max_length=32,null=True,verbose_name="cpu型号")
    cpu = models.CharField(max_length=32,verbose_name="cpu盒数")
    v_or_s = models.CharField(max_length=32,null=True,verbose_name="主机类型")


class Task(models.Model):
    task_group = models.CharField(max_length=256,blank=True)
    hosts = models.CharField(max_length=256,null=True,blank=True)
    cmd = models.TextField(blank=True)
    passwd = models.CharField(max_length=64,null=True,blank=True)
    user = models.CharField(max_length=32,null=True,blank=True)
    status_user = models.BooleanField(default=False,blank=True)
    login = models.BooleanField(default=True,blank=True)
    time = models.DateTimeField(verbose_name="时间", default=timezone.now)

    def __str__(self):
        return self.cmd


class Task_result(models.Model):
    task_id = models.ForeignKey(to="Task",on_delete=models.CASCADE)
    ip = models.CharField(max_length=64,null=True)
    group_name = models.CharField(max_length=64)
    task_status = models.BooleanField()
    message = models.TextField()


class User(models.Model):
    name = models.CharField(max_length=32,null=True,verbose_name="姓名")
    username = models.CharField(max_length=32,verbose_name="系统账号名")
    passwd = models.CharField(max_length=32)
    status = models.CharField(max_length=32)
    push_status = models.CharField(max_length=32,null=True)


############### 权限表

class Group(models.Model):
    name = models.CharField(max_length=32,verbose_name="组名")
    to_control = models.ManyToManyField('Control',verbose_name="权限选择",blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = u'权限组表'


class Control(models.Model):
    code = models.CharField(max_length=32,verbose_name="权限对应代码")
    name = models.CharField(max_length=32,verbose_name="权限名称")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = u'权限表'


class UserInfo(models.Model):
    user = models.CharField(max_length=32)
    passwd = models.CharField(max_length=32)
    name = models.CharField(max_length=32,verbose_name="用户姓名")
    to_group = models.ManyToManyField('Group',verbose_name="组的选择",blank=True)
    to_control = models.ManyToManyField('Control',verbose_name="权限的选择",blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = u'用户权限'