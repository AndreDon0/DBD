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

FULLLOG = False  # Создание файлов для отладки
LOG = True  # Создание файлов для отладки
# Константы
WIDTH, HEIGHT = GetSystemMetrics(0), GetSystemMetrics(1)  # Высота и ширина экрана(с учётом масштаба)
WSCR, HSCR = pag.size()  # Высота и ширина экрана
CENTER = [int(HSCR / 2), int(WSCR / 2)]  # Центр экрана
WHITE = 100  # С какой интенсивности цвета мы его считаем белым


# Проверка нажатия CapsLk
def is_capslock_on():
    return True if ctypes.WinDLL("User32.dll").GetKeyState(0x14) else False


# Нажатие клавиши
def tap(k):
    key.press(k)
    sleep(50 + random() / 20)
    key.release(k)


#  Сделать скриншот
def take_screen(screenshot_region=None):
    if screenshot_region is None:
        screenshot_region = [0, 0, WIDTH, HEIGHT]
    while True:
        screenshot = camera.grab(region=(screenshot_region[0], screenshot_region[1],
                                         screenshot_region[2], screenshot_region[3]))
        if screenshot is not None:
            return screenshot


if LOG:
    # Создание допустимой временной строки
    system_time = str(datetime.datetime.now()).replace(':', '-')
    # Создание папки для хранения скриншотов
    os.makedirs(f'Screenshots/{system_time}', exist_ok=True)
    # Создание txt файла для отчета
    log = open(f"Logs/Log{system_time}.txt", "w")


key.wait("Caps Lock")
camera = dxcam.create(output_color="BGR")
region = [int(CENTER[1] - WIDTH / 20), int(CENTER[0] - HEIGHT / 10),
          int(CENTER[1] + WIDTH / 20), int(CENTER[0] + HEIGHT / 15)]
if LOG:
    log.write(f"Screen size: {WSCR} x {HSCR}")
    log.write(f"Region: left {region[0]}, top {region[1]}, right {region[2]}, bottom {region[3]}")

step = 0
while True:
    while is_capslock_on():
        time_start = time()

        scr = take_screen(region)
        scr_time = time()
        if FULLLOG:
            cv2.imwrite(f"Screenshots/{system_time}/Scr_{step}.png", scr)

        height, width = scr.shape[0:2]
        middle = int(width / 2)
        column = scr[:, middle]
        mask = column > WHITE
        if np.any(mask):
            cir = DbDCircle(scr, scr_time)
            if cir.check_dbd_circle():
                sleep(0.1)
                if LOG:
                    os.makedirs(f'Screenshots/{system_time}/Step{step}', exist_ok=True)
                    cv2.imwrite(f"Screenshots/{system_time}/Step{step}/circle.png", cir.get_image_circle())
                new_scr = take_screen(region)
                new_scr_time = time()
                if LOG:
                    cv2.imwrite(f"Screenshots/{system_time}/Step{step}/new_circle.png", new_scr)
                time_to_tap = cir.calc_time(new_scr, new_scr_time)
                if LOG:
                    log.write(f"Step {step}. Sleep time: {time_to_tap}")

                sleep(time_to_tap)
                tap("space")

        time_end = time()
        step += 1
        step_time = time_end - time_start
        if step % 100 == 0:
            print(f"Step {step}. FPS: {1 / step_time}")
