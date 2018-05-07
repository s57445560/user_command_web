#!/usr/bash
source /etc/profile


start() {
    nohup python service.py >/dev/null 2>&1 &
    echo "start ok ..."
}

stop() {
    ps -ef|grep "python service.py"|grep -v grep|awk '{print $2}'|xargs kill -9 2>/dev/null
    echo "stop ok ..."
}

case "$1" in
  start)
        start
        ;;
  stop)
        stop
        ;;
  restart)
        stop
        start
        ;;
  *)
        echo $"Usage: $prog {start|stop|restart}"
esac