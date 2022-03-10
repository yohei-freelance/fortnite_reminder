#!/bin/sh

echo "[$(date +%s)] START BROADCAST MORNING" >>/home/ec2-user/log/cron_log.log

source linebot/bin/activate
python3 /home/ec2-user/daily.py 2

echo "[$(date +%s)] END BROADCAST MORNING" >>/home/ec2-user/log/cron_log.log
