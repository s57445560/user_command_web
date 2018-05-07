# 更新说明

    此项目会根据使用情况，不定期更新，如有需要沟通可联系QQ：247435333


# 简介

    此平台是 跨平台的账号管理,命令下发,使用。
    使用场景，多平台都是通过vpn来登陆服务器操作的，此时不方便统一管理各平台,
    这时是最适合使用此平台


    
    架构说明：
        
        前端使用：Vue, element-ui, axios
        服务端：django
        客户端：requests，fabric


        client ---> server
        客户端主动向server端请求api，来获取任务，推送数据，为了保证数据安全 之间使用了api认证。

        服务端下发任务，客户端主动获取。


---

# 平台使用说明

## 1、api认证设置 与平台认证

    api认证：

    服务端 execute_task/execute_task/settings.py    内的 APPID 参数是自定义api认证鉴权码
    客户端 client/settings.py                       也有一个 APPID 需要和服务端的配置成一样的鉴权码，否则会认证失败。
    

    平台认证：
    
    服务端：http://192.168.6.125:8008/admin/    内部有一个Groups表，在里面添加平台名称。
                                                只有添加了平台名称客户端才能正常上报。
    客户端：client/settings.py                  参数 QY_NAME 是以什么平台名称来上报数据。

## 2、平台权限管理。

    平台管理的粒度很细，可以针对 各种请求，携带的各种参数，来做认证，也可以针对业务来做认证。

    execute_task/task/permission_list.py 是权限管理的条目, 它是一个字典。

    字典解析：
    
       command_post_cmd 权限对应的自定义代码，在admin内设置权限时使用
       command 是url.py内对应的url name 
       POST 指定是什么请求
       [] 需要携带什么参数
       {"status":"cmd"} 明确指定携带参数的value是什么
       custom_perm_logic.only_view_own_customers 是权限自定义钩子，可以针对自己的业务来自定义权限，返回True/False
 
    'command_post_cmd': ['command', 'POST', [], {"status":"cmd"}, custom_perm_logic.only_view_own_customers]

    使用方法：
        在admin内打开，设置权限条目，设置用户组，和用户，来对其进行权限控制。


## 3、平台部署

    服务端安装：
        默认使用的数据库是 sqlit3,如需更换请自行修改配置，python需要使用 3

    客户端安装：
        安装fabric模块和 requsts模块即可。
        启动： bash start.sh start 



## 平台展示

#### 登陆页面

![image](https://github.com/s57445560/img-all/raw/master/user_command/login.png)


#### 主页面

![image](https://github.com/s57445560/img-all/raw/master/user_command/index.png)


#### 用户页面

![image](https://github.com/s57445560/img-all/raw/master/user_command/user_list.png)


#### 命令执行

![image](https://github.com/s57445560/img-all/raw/master/user_command/command.png)

![image](https://github.com/s57445560/img-all/raw/master/user_command/command1.png)


#### admin后台groups管理与权限控制

![image](https://github.com/s57445560/img-all/raw/master/user_command/admin_groups.png)

![image](https://github.com/s57445560/img-all/raw/master/user_command/jq.png)
