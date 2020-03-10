#!/bin/bash
source /home/ubuntu/stringkeeper/bin/activate && cd /home/ubuntu/stringkeeper/ && python manage.py process_tasks >> /home/ubuntu/stringkeeper/background_task.log