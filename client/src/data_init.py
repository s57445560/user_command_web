#!/usr/bin/python
# coding=utf8



def run():
    list_user_ip = []
    ip_dict = {}
    with open('data/ip.conf') as f:
        for line in f.readlines():
            if line.rstrip() == '':
                continue
            list_line = line.rstrip().split()
            ip = list_line[0]
            passwd = list_line[1]
            ip_dict['root@' + ip + ':22'] = passwd
            ssh_ip = ip
            list_user_ip.append(ssh_ip)
    return (list_user_ip,ip_dict)


if __name__ == '__main__':
    run()