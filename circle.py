import numpy as np
import cv2
from math import sin, cos, pi, inf

SIZE = 180  # Размер массива круга
WHITE = 100  # С какой интенсивности цвета мы его считаем белым
RED = 200  # С какой интенсивности цвета мы его считаем красным
GOOD = 10  # Если интенсивность цвета ниже, то считаем эту зону хорошей проверкой реакции
EXCELLENT = 250  # Если интенсивность цвета выше, то считаем эту зону хорошей проверкой реакции
CORRECT_LENGTH = int(SIZE / 60)  # Длинна при которой мы считаем скопление точек регионом


# Круг, представимый в виде массива
class Circle:
    def __init__(
            self,
            centre: list,
            radius: int,
            t: float,
            size: int,
    ) -> None:
        self.centre = centre
        self.radius = radius
        self.size = size
        self.t = t
        self.circle = np.empty(size)

    # Из индекса массива возвращает угол
    def from_size_to_phi(self, i: int) -> float:
        return i % self.size / self.size * 2 * pi

    # Из массива индексов возвращает массив углов
    def from_areas_to_phi(self, areas: list) -> list:
        for i in range(0, len(areas)):
            areas[i][0] = self.from_size_to_phi(areas[i][0])
            areas[i][1] = self.from_size_to_phi(areas[i][1])
        return areas

    # Зная угол, возвращает ЦЕЛОЧИСЛЕННЫЕ декартовы координаты
    def coordinate(self, pfi: float) -> list:
        return [self.centre[0] + int(self.radius * cos(pfi)),
                self.centre[1] + int(self.radius * sin(pfi))]

    # Из картинки читает линию круга
    def circling_image(self, image: np.ndarray) -> None:
        for i in range(0, self.size):
            phi = self.from_size_to_phi(i)
            y, x = self.coordinate(phi)
            self.circle[i] = image[y, x]

    # Вывод индексов подходящих участков
    @staticmethod
    def find_true_areas(
            array: np.ndarray,
            cor_len: int
    ) -> list:
        true_regions = []
        area = [0, 0]
        array = np.append(array, [False])

        beg = False
        for i, bool_value in enumerate(array):
            if beg:
                if bool_value:
                    area[1] = i
                else:
                    if area[1] - area[0] + 1 > cor_len:
                        true_regions.append(area.copy())
                    beg = False
            else:
                if bool_value:
                    beg = True
                    area[0] = i
                    area[1] = i

        return true_regions

    # Если в какой-то области круга значения больше чем
    # введённое, вывести начало и конец наибольшей области
    def more_then(
            self,
            other: int,
            cor_len: int = CORRECT_LENGTH
    ) -> list:
        areas = self.circle > other
        true_regions = self.find_true_areas(areas, cor_len=cor_len)
        true_regions_phi = self.from_areas_to_phi(true_regions)
        return true_regions_phi

    # Если в какой-то области круга значения меньше чем
    # введённое, вывести начало и конец наибольшей области
    def less_then(
            self,
            other: int,
            cor_len: int = CORRECT_LENGTH
    ) -> list:
        areas = self.circle < other
        true_regions = self.find_true_areas(areas, cor_len=cor_len)
        true_regions_phi = self.from_areas_to_phi(true_regions)
        return true_regions_phi


class DbDCircle:
    # Возвращает центр круга и его радиус
    @staticmethod
    def calc_cen_rad_circle(
            image: np.ndarray,
            white: int = WHITE,
            math: bool = False
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

        if not math and bottom < height:  # Подгон значений
            bottom += 1
        x0, y0 = middle, int((top + bottom) / 2)
        rad = int((bottom - top) / 2)
        center = [y0, x0]
        return [center, rad]

    def __init__(
            self,
            image: np.ndarray,
            t: float,
            size: int = SIZE,
    ) -> None:

        # Создание разный видов картинки
        self.image = image
        self.grey_img = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        self.object_img = self.create_obg_image(image)

        # Задание математических параметров
        self.center, self.radius = self.calc_cen_rad_circle(self.grey_img)

        # Создание круга
        self.size = size
        self.time_start = t
        self.grey_circle = Circle(self.center, self.radius, t, size)
        self.object_circle = Circle(self.center, self.radius, t, size)
        self.grey_circle.circling_image(self.grey_img)
        self.object_circle.circling_image(self.object_img)

        # Задание изначальной позиции объекта
        self.object_position = self.object_circle.more_then(RED, cor_len=0)

        # Задание позиции хорошей и отличной зон
        self.excellent_position = self.grey_circle.more_then(EXCELLENT)
        self.good_position = self.grey_circle.less_then(GOOD)

    # Создание картинки на которой объект четко выделен
    @staticmethod
    def create_obg_image(image: np.ndarray) -> np.ndarray:
        b, g, r = cv2.split(image)
        return np.array(r, np.int16) - np.array(g, np.int16) - np.array(b, np.int16)

    # Поиск минимального времени для пересечения указателя и окрестности
    @staticmethod
    def find_time_to_areas(areas: list, om: float) -> float:
        min_time = inf
        for area in areas:
            p1 = (area[1] - area[0]) / 2
            p2 = p1 - 2 * pi
            t1 = p1 / om
            t2 = p2 / om
            tm = min(t1, t2)
            if min_time < tm:
                min_time = tm

        return min_time

    def calc_time(self, new_image: np.ndarray, t: float) -> float:
        b, g, r = cv2.split(new_image)
        new_object_img = (np.array(r, np.int16) - np.array(g, np.int16) - np.array(b, np.int16))
        new_object_circle = Circle(self.center, self.radius, t, self.size)
        new_object_circle.circling_image(new_object_img)
        new_object_position = new_object_circle.more_then(RED)

        phi0 = self.object_position[0][1] - self.object_position[0][0]
        phi1 = new_object_position[0][1] - new_object_position[0][0]
        time0 = self.object_circle.t
        time1 = t
        om = (phi1 - phi0) / (time1 - time0)

        if not self.excellent_position == []:
            return self.find_time_to_areas(self.excellent_position, om)
        elif not self.good_position == []:
            return self.find_time_to_areas(self.good_position, om)
        else:
            raise ValueError("Не найдено ни хорошей ни отличной позиции")

    # Проверка круга на то что бы он был из дбд
    def check_dbd_circle(self) -> bool:
        check_obj = (not self.object_position == [])
        check_ex = (not self.excellent_position == [])
        check_good = (not self.good_position == [])
        check_circle = bool(sum(self.grey_circle.circle > WHITE) > (SIZE / 4))

        return check_obj and (check_ex or check_good) and check_circle

    # Вывод рисунка с помеченной окружностью
    def get_image_circle(self) -> np.ndarray:
        mod_img = self.image
        for i in range(0, self.grey_circle.size):
            phi = self.grey_circle.from_size_to_phi(i)
            y, x = self.grey_circle.coordinate(phi)
            mod_img[y, x] = 255
        return mod_img
