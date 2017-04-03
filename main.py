# -*- coding: utf-8 -*-
import sys
import time
from adxl345 import ADXL345

check_time = 10  # sec
sleep_time = 0.1
threshold = 0.03

queue_size = int(check_time / sleep_time)

def last_list(lis, value):
    lis.append(value)
    if len(lis) >= queue_size + 1:
        lis = lis[1:]
    return lis

adxl345 = ADXL345()
axes = adxl345.getAxes(True)
base = (axes['x'], axes['y'], axes['z'])

last_10_value = [base] * queue_size
last_10_check = [False] * queue_size

while True:
    axes = adxl345.getAxes(True)
    x = axes['x']
    y = axes['y']
    z = axes['z']

    diff_x = abs(last_10_value[-1][0] - x)
    diff_y = abs(last_10_value[-1][1] - y)
    diff_z = abs(last_10_value[-1][2] - z)

    check = diff_x > threshold or diff_y > threshold or diff_z > threshold

    last_10_value = last_list(last_10_value, (x, y, z))
    last_10_check = last_list(last_10_check, check)

    if check:
        print(x, y, z)

    time.sleep(sleep_time)

