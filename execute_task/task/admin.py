from django.contrib import admin

# Register your models here.

from task import models

class ArticleAdmin(admin.ModelAdmin):
    list_display = ('id', 'name',) 			# 设置多字段显示
    list_filter = ('name',)					# 显示过滤字段
    search_fields = ('name',)					# 设置搜索页面里可以搜索的字段


class TaskAdmin(admin.ModelAdmin):
    list_display = ('id', 'task_group','cmd','user',) 			# 设置多字段显示
    list_filter = ('task_group','cmd',)					# 显示过滤字段
    search_fields = ('user',)					# 设置搜索页面里可以搜索的字段


class Task_resultAdmin(admin.ModelAdmin):
    list_display = ('id', 'group_name','task_id','task_status',) 			# 设置多字段显示
    list_filter = ('group_name','task_id',)					# 显示过滤字段
    search_fields = ('group_name',)					# 设置搜索页面里可以搜索的字段



class UserInfoAdmin(admin.ModelAdmin):
    filter_horizontal = ('to_group', 'to_control')


admin.site.register(models.UserInfo,UserInfoAdmin)
admin.site.register(models.Control)
admin.site.register(models.Group)
admin.site.register(models.Groups,ArticleAdmin)
admin.site.register(models.Task,TaskAdmin)
admin.site.register(models.Task_result,Task_resultAdmin)