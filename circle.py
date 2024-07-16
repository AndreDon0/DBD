import numpy as np
import cv2
from time import time
from math import sin, cos, pi

SIZE = 360
WHITE = 100
RED = 200
GOOD = 10
EXCELLENT = 250


# Круг, представимый в виде массива
class Circle:
    def __init__(
            self,
            centre: list,
            radius: int,
            t: float,
            size: int = SIZE,
    ) -> None:
        self.centre = centre
        self.radius = radius
        self.circle = np.empty(SIZE)
        self.size = size
        self.t = t

    # Из индекса массива возвращает угол
    def from_size_to_phi(self, i: int) -> float:
        return i / self.size * 2 * pi

    # Зная угол, возвращает ЦЕЛОЧИСЛЕННЫЕ декартовы координаты
    def coordinate(self, pfi: int) -> list:
        return [self.centre[0] + int(self.radius * cos(pfi)),
                self.centre[1] + int(self.radius * sin(pfi))]

    # Из картинки читает линию круга
    def circling_image(self, image):
        for i in range(0, self.size):
            phi = self.from_size_to_phi(i)
            y, x = self.coordinate(phi)
            self.circle[i] = image[y, x]

    def to_array(self) -> np.ndarray:
        return self.circle

    # Возвращает максимальный по длине массив массива
    @staticmethod
    def max_len(arr: list) -> list:
        m = []
        for i in arr:
            if len(i) > len(m):
                m = i
        return m

    # Если в какой-то области круга значения больше чем
    # введённое, вывести начало и конец наибольшей области
    def more_then(self, other: int) -> float:
        areas = self.circle > other
        max_area = [0, 0]
        area = [0, 0]
        p = False
        for i, bool_value in enumerate(areas):
            if bool_value and p:
                area[0] = i
                p = True
            else:
                area[1] = i - 1
                p = False
                if area[1] - area[0] > max_area[1] - max_area[0]:
                    max_area = area

        max_area[0] = self.from_size_to_phi(max_area[0])
        max_area[1] = self.from_size_to_phi(max_area[1])
        return (max_area[0] + max_area[1]) / 2

    # Если в какой-то области круга значения меньше чем
    # введённое, вывести начало и конец наибольшей области
    def less_then(self, other: int) -> float:
        areas = self.circle < other
        max_area = [0, 0]
        area = [0, 0]
        p = False
        for i, bool_value in enumerate(areas):
            if bool_value and p:
                area[0] = i
                p = True
            else:
                area[1] = i - 1
                p = False
                if area[1] - area[0] > max_area[1] - max_area[0]:
                    max_area = area

        max_area[0] = self.from_size_to_phi(max_area[0])
        max_area[1] = self.from_size_to_phi(max_area[1])
        return (max_area[0] + max_area[1]) / 2


class DbDCircle:
    # Возвращает центр круга и его радиус
    @staticmethod
    def CRcircle(
            image: np.ndarray,
            white: int = WHITE
    ) -> list:

        height, width = image.shape[0:2]
        middle = int(width / 2)
        column = image[:, middle]
        top, bottom = height, 0
        for i in range(0, len(column)):
            pixel = column[i]
            if pixel > white:
                if i < top:
                    top = i
                if i > bottom:
                    bottom = i

        x0, y0 = middle, int((top + bottom) / 2)
        center = [x0, y0]
        radius = int((bottom - top) / 2)
        return [center, radius]

    def __init__(
            self,
            image: np.ndarray,
            t: float,
            size: int = SIZE,
    ) -> None:

        # Создание разный видов картинки
        self.Gimg = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        b, g, r = cv2.split(image)
        self.Oimg = (np.array(r, np.int16) - np.array(g, np.int16) - np.array(b, np.int16))

        # Задание математических параметров
        self.center, self.radius = self.CRcircle(self.Gimg)

        # Создание круга
        self.size = size
        self.time_start = t
        self.Gcircle = Circle(self.center, self.radius, t, size)
        self.Ocircle = Circle(self.center, self.radius, t, size)
        self.Gcircle.circling_image(self.Gimg)
        self.Ocircle.circling_image(self.Oimg)

        # Задание изначальной позиции объекта
        self.Oposition = self.Ocircle.more_then(RED)

        # Задание позиции хорошей и отличной зон
        self.Eposition = self.Gcircle.more_then(EXCELLENT)
        self.Gposition = self.Gcircle.less_then(GOOD)

    def calc_time(self, image: np.ndarray, t: float) -> float:
        b, g, r = cv2.split(image)
        new_Oimg = (np.array(r, np.int16) - np.array(g, np.int16) - np.array(b, np.int16))
        new_Ocircle = Circle(self.center, self.radius, t, self.size)
        new_Ocircle.circling_image(new_Oimg)
        new_Oposition = new_Ocircle.more_then(RED)

        phi0 = self.Oposition
        phi1 = new_Oposition
        t0 = self.Ocircle.t
        t1 = t
        om = (phi1 - phi0) / (t1 - t0)
        if self.Eposition != 0:
            return self.Eposition / om
        elif self.Gposition != 0:
            return self.Gposition / om
        else:
            raise ValueError("Не найдено ни хорошей ни отличной позиции")


