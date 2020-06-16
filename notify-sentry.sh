#!/bin/sh

PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
PYTHONPATH=/usr/lib/python37.zip:/usr/lib/python3.7:/usr/lib/python3.7/lib-dynload:/home/pi/.local/lib/python3.7/site-packages:/usr/local/lib/python3.7/dist-packages:/usr/lib/python3/dist-packages
PYHOME=/home/pi/python

export PATH
export PYTHONPATH
export PYHOME
/usr/bin/python3 $PYHOME/notification.py --debug info >> /home/pi/logs/notify-sentry.log 2>&1 &
