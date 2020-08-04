#!/bin/sh

dir=`dirname $0`
setenv=$dir/set-env.sh

if [ ! -f $setenv ]
then
   echo "Could not find file $setenv" >> /home/pi/logs/notify-sentry.log
else
   . $setenv
   /usr/bin/python3 $PYHOME/notification.py --debug info >> /home/pi/logs/notify-sentry.log 2>&1 &
fi


