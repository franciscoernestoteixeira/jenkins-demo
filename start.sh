#!/bin/bash
cd /opt/jenkins-demo
setsid .venv/bin/uvicorn main:app --host 0.0.0.0 --port 80 > /tmp/app.log 2>&1 < /dev/null &