#!/bin/sh

echo "[$(date +%s)] START FINALIZE TABLE" >>/home/ec2-user/log/cron_log.log

source linebot/bin/activate
python3 /home/ec2-user/daily.py 4

echo "[$(date +%s)] END FINALIZE TABLE" >>/home/ec2-user/log/cron_log.log
