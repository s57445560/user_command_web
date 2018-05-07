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

## api认证设置 与平台认证

    api认证：

    服务端 execute_task/execute_task/settings.py    内的 APPID 参数是自定义api认证鉴权码
    客户端 client/settings.py                       也有一个 APPID 需要和服务端的配置成一样的鉴权码，否则会认证失败。
    

    平台认证：
    
    服务端：http://192.168.6.125:8008/admin/    内部有一个Groups表，在里面添加平台名称。只有添加了平台名称客户端才能正常上报。
    客户端：client/settings.py                  参数 QY_NAME 是以什么平台名称来上报数据。


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
