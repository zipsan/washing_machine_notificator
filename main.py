# -*- coding: utf-8 -*-
import sys
import time
from adxl345 import ADXL345
from datetime import datetime


check_time = 2  # [sec]
sleep_time = 0.1  # [sec]
finish_time = 10  # [sec] この秒数間揺れがなかったら終了とみなす
t_shake = 0.03
t_count = 8  # max: check_time / sleep_time
t_shake_count = 3

queue_size = int(check_time / sleep_time)

adxl345 = ADXL345()
axes = adxl345.getAxes(True)
base = (axes['x'], axes['y'], axes['z'])

measureing = False
time_count = 0
shake_count = 0


def last_list(lis, value):
    lis.append(value)
    if len(lis) >= queue_size + 1:
        lis = lis[1:]
    return lis


def reset_list(value):
    return [value] * queue_size


def is_shaking():
    return sum(last_10_check) >= t_count


def write_char(c):
    sys.stdout.write(c)
    sys.stdout.flush()


last_10_value = reset_list(base)
last_10_check = reset_list(False)

while True:
    axes = adxl345.getAxes(True)
    x = axes['x']
    y = axes['y']
    z = axes['z']

    diff_x = abs(last_10_value[-1][0] - x)
    diff_y = abs(last_10_value[-1][1] - y)
    diff_z = abs(last_10_value[-1][2] - z)

    check = diff_x > t_shake or diff_y > t_shake or diff_z > t_shake

    last_10_value = last_list(last_10_value, (x, y, z))
    last_10_check = last_list(last_10_check, check)

    if time_count % (check_time / sleep_time) == 0:
        if not measureing and not is_shaking():
            # 待機状態
            shake_count = 0
            write_char("_")

        elif not measureing and is_shaking():
            # 計測してないときに検知したら計測中に変更
            shake_count += 1
            if shake_count >= t_shake_count:
                write_char("S")
                measureing = True
                start_time = datetime.now()  # 開始時間を記録
            else:
                write_char("-")
            interval_start_time = datetime.now()  # 最後の揺れ時間を記録する

        elif measureing and is_shaking():
            # 計測中に検知したら時間を更新
            write_char(".")
            interval_start_time = datetime.now()

        elif measureing and not is_shaking():
            # 計測中に検知しなくなったら（終了したorインターバルタイムのとき）
            timedelta = datetime.now() - interval_start_time
            if timedelta.total_seconds() >= finish_time:
                # 終了した
                write_char("E")
                measureing = False
                last_10_check = reset_list(False)
                last_10_value = reset_list(base)

            else:
                write_char("x")
                # まだ終わってない場合はインターバルタイムで停止しているとみなす
                pass

        if is_shaking():
            # 検知したらリストを初期化
            last_10_check = reset_list(False)
            last_10_value = reset_list(base)

    time_count += 1
    time.sleep(sleep_time)
