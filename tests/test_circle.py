import cv2
from time import time
from math import pi
import numpy as np
import matplotlib.pyplot as plt
from circle import Circle, DbDCircle

SIZE = 360  # Размер массива круга
WHITE = 100  # С какой интенсивности цвета мы его считаем белым
RED = 200  # С какой интенсивности цвета мы его считаем красным
GOOD = 10  # Если интенсивность цвета ниже, то считаем эту зону хорошей проверкой реакции
EXCELLENT = 250  # Если интенсивность цвета выше, то считаем эту зону хорошей проверкой реакции
CORRECT_LENGTH = int(SIZE / 180)  # Длинна при которой мы считаем скопление точек регионом


class TestCircle:
    centre = [1, 1]
    radius = 1
    t = time()
    circle = Circle(centre, radius, t, size=4)

    def test_init(self):
        assert self.circle.circle.size == 4

    def test_to_phi1(self):
        assert self.circle.from_size_to_phi(1) == pi / 2

    def test_to_phi2(self):
        assert self.circle.from_size_to_phi(2) == pi

    def test_to_phi3(self):
        assert self.circle.from_size_to_phi(5) == pi / 2

    def test_to_phi4(self):
        assert self.circle.from_size_to_phi(-1) == 3 * pi / 2

    def test_areas_to_phi1(self):
        assert self.circle.from_areas_to_phi([[0, 2]]) == [[0, pi]]

    def test_areas_to_phi2(self):
        assert self.circle.from_areas_to_phi([[0, 1], [2, 3]]) == [[0, pi / 2], [pi, 3 * pi / 2]]

    def test_coordinate1(self):
        assert self.circle.coordinate(0) == [2, 1]

    def test_coordinate2(self):
        assert self.circle.coordinate(pi / 2) == [1, 2]

    circle.circle = np.array([0, 100, 200, 255])

    def test_true_areas1(self):
        arr = np.array([False, True, False])
        areas = self.circle.find_true_areas(arr, cor_len=1)
        assert areas == []

    def test_true_areas2(self):
        arr = np.array([True, True, True, True, False, True, True, False, False, False, True, True])
        areas = self.circle.find_true_areas(arr, cor_len=1)
        assert areas == [[0, 3], [5, 6], [10, 11]]

    def test_less_then1(self):
        areas = self.circle.less_then(150, cor_len=1)
        assert areas == [[0, pi / 2]]

    def test_less_then2(self):
        areas = self.circle.less_then(250, cor_len=1)
        assert areas == [[0, pi]]

    def test_more_then1(self):
        areas = self.circle.more_then(100, cor_len=1)
        assert areas == [[pi, 3 * pi / 2]]

    def test_more_then2(self):
        areas = self.circle.more_then(50, cor_len=1)
        assert areas == [[pi / 2, 3 * pi / 2]]


class TestDbDCircle:
    image = np.array([[0, 255, 255, 255, 0],
                      [255, 0, 0, 0, 255],
                      [255, 0, 0, 0, 255],
                      [255, 0, 0, 0, 255],
                      [0, 255, 255, 255, 0]])
    scr = cv2.imread("../Screenshots/Scr.png")
    t = time()
    dbd_circle = DbDCircle(scr, t)

    @staticmethod
    def calc_cen_rad_circle(
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
        center = [y0, x0]
        rad = int((bottom - top) / 2)
        return [middle, height, [top, bottom], center, rad]

    buf = calc_cen_rad_circle(dbd_circle.grey_img)
    middle, height, tb, center, rad = buf[0], buf[1], buf[2], buf[3], buf[4]
    yc, xc = center[0], center[1]
    top, bottom = tb[0], tb[1]

    def test_cr_calc1(self):
        buf = DbDCircle.calc_cen_rad_circle(self.image, math=True)
        center = buf[0]
        assert center == [2, 2]

    def test_cr_calc2(self):
        buf = DbDCircle.calc_cen_rad_circle(self.image, math=True)
        radius = buf[1]
        assert radius == 2

    def test_cr_calc3(self):
        assert ((self.xc == self.middle) and
                (self.top == self.yc - self.rad) and
                (self.bottom == self.yc + self.rad + 1))
"""
    def test_cr_calc4(self):  # Проверяется вручную
        print()
        print(self.center, self.rad)

        def draw_line(image, point1, point2):
            x_values = np.linspace(point1[1], point2[1], num=1000)
            y_values = np.linspace(point1[0], point2[0], num=1000)

            for i in range(len(x_values)):
                x = int(x_values[i])
                y = int(y_values[i])
                image[y, x] = 255

        def draw_point(image, point):
            image[point[0], point[1]] = 0

        mod_img = self.scr
        draw_line(mod_img, [0, self.middle], [self.height - 1, self.middle])
        draw_point(mod_img, [self.top, self.middle])
        draw_point(mod_img, [self.bottom, self.middle])
        draw_point(mod_img, self.center)

        plt.imshow(mod_img, cmap='gray')
        plt.axis('off')
        plt.show()

    def test_circle(self):  # Проверяется вручную
        mod_img = self.dbd_circle.get_image_circle()
        plt.imshow(mod_img, cmap='gray')
        plt.axis('off')
        plt.show()

    def test_obj_circle(self):  # Проверяется вручную
        mod_img = self.scr
        Ocircle = self.dbd_circle.object_circle
        obj_pos = self.dbd_circle.object_position
        print()
        print(obj_pos)
        for i in range(0, len(obj_pos)):
            y1, x1 = Ocircle.coordinate(obj_pos[i][0])
            y2, x2 = Ocircle.coordinate(obj_pos[i][1])
            print(x1, y1)
            print(x2, y2)
            mod_img[y1, x1] = 255
            mod_img[y2, x2] = 255
        plt.imshow(mod_img, cmap='gray')
        plt.axis('off')
        plt.show()

    def test_excellent(self):  # Проверяется вручную
        mod_img = self.scr
        Gcircle = self.dbd_circle.object_circle
        ex_pos = self.dbd_circle.excellent_position
        print()
        print(ex_pos)
        for i in range(0, len(ex_pos)):
            y1, x1 = Gcircle.coordinate(ex_pos[i][0])
            y2, x2 = Gcircle.coordinate(ex_pos[i][1])
            print(x1, y1)
            print(x2, y2)
            mod_img[y1, x1] = 0
            mod_img[y2, x2] = 0
        plt.imshow(mod_img, cmap='gray')
        plt.axis('off')
        plt.show()

    def test_good(self):  # Проверяется вручную
        mod_img = self.scr
        Gcircle = self.dbd_circle.object_circle
        good_pos = self.dbd_circle.good_position
        print()
        print(good_pos)
        for i in range(0, len(good_pos)):
            y1, x1 = Gcircle.coordinate(good_pos[i][0])
            y2, x2 = Gcircle.coordinate(good_pos[i][1])
            print(x1, y1)
            print(x2, y2)
            mod_img[y1, x1] = 255
            mod_img[y2, x2] = 255
        plt.imshow(mod_img, cmap='gray')
        plt.axis('off')
        plt.show()

    def test_check(self):
        assert self.dbd_circle.check_dbd_circle() is True
"""
