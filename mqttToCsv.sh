#!/usr/bin/sh

cd /home/pi/scripts
. .venv/bin/activate
python -V
while true; do
  date
  python mqttToCsv.py
  ls -ltr /home/pi/data/*.csv | tail -n 2
done
