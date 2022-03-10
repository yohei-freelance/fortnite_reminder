#!/bin/sh

echo "[$(date +%s)] START BROADCAST EVENING" >>/home/ec2-user/log/cron_log.log

source linebot/bin/activate
python3 /home/ec2-user/daily.py 3

echo "[$(date +%s)] END BROADCAST EVENING" >>/home/ec2-user/log/cron_log.log
