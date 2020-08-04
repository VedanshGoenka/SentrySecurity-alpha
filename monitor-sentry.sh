#!/bin/sh

dir=`dirname $0`
setenv=$dir/set-env.sh

if [ ! -f $setenv ]
then
   echo "Could not find file $setenv" >> /home/pi/logs/sentry.log
else
   . $setenv
   sudo -u pi -g pi --preserve-env=PYHOME /usr/bin/python3 $PYHOME/monitor.py >> /home/pi/logs/sentry.log 2>&1 &
fi
