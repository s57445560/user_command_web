"""execute_task URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from task import views

urlpatterns = [
    url(r'Get_put_task/', views.Get_put_task.as_view(),name="Get_put_task"),
    url(r'host/', views.Host_info.as_view(),name="Host_info"),
    url(r'login/', views.Login.as_view(),name="Login"),
    url(r'logout/', views.Logout,name="Logout"),
    url(r'task_info/', views.Task_info.as_view(), name="task_info"),
    url(r'Get_taskid_all/', views.Get_taskid_all.as_view(),name="Get_taskid_all"),
    url(r'Monitor_status/', views.Monitor_status.as_view(), name="Monitor_status"),
    url(r'index/', views.Index.as_view(), name="index"),
    url(r'command/', views.Command.as_view(), name="command"),
    url(r'user/edit/', views.User_edit.as_view(), name="user_edit"),
    url(r'user/del/', views.User_del.as_view(), name="user_del"),
    url(r'user/', views.User.as_view(), name="user"),
    url(r'user_list/', views.User_list.as_view(), name="user_list"),

]
