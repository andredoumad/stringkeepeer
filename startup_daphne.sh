#!/bin/bash
source /home/ubuntu/stringkeeper/bin/activate && cd /home/ubuntu/stringkeeper && daphne -b 0.0.0.0 -p 8001 stringkeeper.asgi:application