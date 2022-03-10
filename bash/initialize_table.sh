#!/bin/sh

echo "[$(date +%s)] START INITIALIZE TABLE" >>/home/ec2-user/log/cron_log.log

source linebot/bin/activate
python3 /home/ec2-user/daily.py 1

echo "[$(date +%s)] END INITIALIZE TABLE" >>/home/ec2-user/log/cron_log.log
