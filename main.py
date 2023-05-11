
from PIL import Image, ImageShow, ImageDraw
import math


class MainBoard:
    width = 0
    height = 0
    gridDivisionSize = 0
    image = Image
    elements = []

    def paint_elements(self):
        if len(self.elements) != 0:
            for i in self.elements:
                i.paint_element(self.image, self.gridDivisionSize)

    def paint_grid(self):
        image_grid = ImageDraw.Draw(self.image)
        num_steps_horizontal = math.ceil(self.height/self.gridDivisionSize)
        num_steps_vertical = math.ceil(self.width/self.gridDivisionSize)
        for i in range(0, num_steps_vertical+1):
            start_horizontal_position = [(i*self.gridDivisionSize, 0), (i*self.gridDivisionSize, self.height )]
            image_grid.line(start_horizontal_position, 1)
        for j in range(0, num_steps_horizontal+1):
            start_vertical_position = [(0, j*self.gridDivisionSize), (self.width, j*self.gridDivisionSize)]
            image_grid.line(start_vertical_position, 1)

    def paint_board(self):
        self.image = Image.new("RGB", (self.width, self.height), (0, 255, 0))

    def append_new_element(self, x_c, y_c, h, w):
        self.elements.append(BoardElement(x_c, y_c, h, w))

    def show_board(self):
        self.paint_elements()
        ImageShow.show(self.image, "Board")

    def __init__(self, user_width, user_height, user_grid):
        self.width = user_width
        self.height = user_height
        self.gridDivisionSize = user_grid
        self.paint_board()
        self.paint_grid()


class BoardElement:
    x_c = 0         #Расположение центра элемента ось oX
    y_c = 0         #Расположение центра элемента ось oY
    h = 0           #Высота элемента
    w = 0           #Ширина элемента

    def __init__(self, x, y, h, w):
        self.x_c = x
        self.y_c = y
        self.h = h
        self.w = w

    def paint_element(self, image, grid_size):
        image_print_element = ImageDraw.Draw(image)
        x_low_pos = (self.x_c - self.w/2)*grid_size
        y_low_pos = (self.y_c - self.h/2)*grid_size
        x_high_pos = (self.x_c + self.w/2)*grid_size
        y_high_pos = (self.y_c + self.h/2)*grid_size
        element_position = (x_low_pos, y_low_pos, x_high_pos, y_high_pos)
        image_print_element.rectangle(xy=element_position, fill=(255, 255, 0), outline="red")


if __name__ == '__main__':
    new_board = MainBoard(500, 1000, 10)
    new_board.append_new_element(10, 15, 3, 3)
    new_board.append_new_element(30, 40, 3, 7)
    new_board.append_new_element(16, 20, 1, 1)
    new_board.show_board()
