import ctypes
from random import random
import dxcam
import pyautogui as pag
import keyboard as key
import numpy as np
from time import time, sleep
import cv2
import os
import datetime
from win32api import GetSystemMetrics
from circle import DbDCircle

# Константы
LOG = True
WIDTH, HEIGHT = GetSystemMetrics(0), GetSystemMetrics(1)  # Высота и ширина экрана(с учётом масштаба)
WSCR, HSCR = pag.size()  # Высота и ширина экрана
CENTER = [int(WSCR / 2), int(HSCR / 2)]  # Центр экрана
SIZE = 360  # Размер круга
WHITE = 100  # С какой интенсивности цвета мы его считаем белым
RED = 100  # С какой интенсивности цвета мы его считаем красным


# Проверка нажатия CapsLk
def is_capslock_on():
    return True if ctypes.WinDLL("User32.dll").GetKeyState(0x14) else False

# Нажатие клавиши
def tap(k):
    key.press(k)
    sleep(random() / 50)
    key.release(k)

#  Сделать скриншот
def take_screen(scr_region=None):
    if scr_region is None:
        scr_region = [0, 0, WIDTH, HEIGHT]
    while True:
        scr = camera.grab(region=(scr_region[0], scr_region[1], scr_region[2], scr_region[3]))
        if scr is not None:
            return scr


if LOG:
    # Поиск пути до проекта и создание допустимой временной строки
    """
    path = abspath(__file__).replace('\\', '/')
    path = path[:path.rfind("/")]
    """
    t = str(datetime.datetime.now()).replace(':', '-')

    # Создание рабочих папок
    os.makedirs(f'Screenshots/{t}', exist_ok=True)

key.wait("Caps Lock")
camera = dxcam.create(output_color="BGR")
region = [int(CENTER[1] - WSCR / 20), int(CENTER[1] + WSCR / 20),
          int(CENTER[0] - HSCR / 10), int(CENTER[0] + HSCR / 15)]
step = 0
while True:
    while is_capslock_on():
        time_start = time()

        scr = take_screen(region)
        scr_time = time()

        height, width = scr.shape[0:2]
        middle = int(width / 2)
        column = scr[:, middle]
        mask = column > WHITE
        if np.any(mask):
            cir = DbDCircle(scr, scr_time)
            sleep(0.01)
            new_scr = take_screen(region)
            new_scr_time = time()
            time_to_tap = cir.calc_time(new_scr, new_scr_time)

            if LOG:
                cv2.imwrite("Scr.png", scr)
            sleep(time_to_tap)
            tap("space")
            print(time_to_tap)

        time_end = time()
        step += 1
        step_time = time_end - time_start
        print(f"Step {step}. FPS: {1 / step_time} Execution time: {step_time}")
