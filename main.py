
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

    def append_element(self, instance, x_c, y_c):
        instance.grid_size = self.gridDivisionSize
        instance.x_c = x_c
        instance.y_c = y_c
        instance.append_pins(instance.spm)
        self.elements.append(instance)

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
    pin = []        #Пины к которым идет
    grid_size = 0   #Размер сетки
    spm = []

    def __init__(self, x, y, h, w, grid_size):
        self.x_c = x
        self.y_c = y
        self.h = h
        self.w = w
        self.grid_size = grid_size

    def paint_element(self, image, grid_size):
        image_print_element = ImageDraw.Draw(image)
        x_low_pos = (self.x_c - self.w/2)*grid_size
        y_low_pos = (self.y_c - self.h/2)*grid_size
        x_high_pos = (self.x_c + self.w/2)*grid_size
        y_high_pos = (self.y_c + self.h/2)*grid_size
        element_position = (x_low_pos, y_low_pos, x_high_pos, y_high_pos)
        image_print_element.rectangle(xy=element_position, fill=(255, 255, 0), outline="red")
        for i in self.pin:
            i.paint_pin(image_print_element, grid_size)

    def append_pins(self, locations_places):
        for i in locations_places:
            self.append_new_pin(i[0], i[1], i[2])

    def append_new_pin(self, location, place_pin, connect_pins):
        if len(place_pin) != 0:
            if location == "right":
                for i in place_pin:
                    x_pin = self.x_c + self.w/2 - 0.25
                    y_pin = self.y_c - math.ceil((self.h/2)/self.grid_size) + (i-1) - 0.225
                    self.pin.append(Pin(x_pin, y_pin, connect_pins))
            elif location == "left":
                for i in place_pin:
                    x_pin = self.x_c - self.w/2 - 0.25
                    y_pin = self.y_c - math.ceil((self.h/2)/self.grid_size) + (i-1) - 0.225
                    self.pin.append(Pin(x_pin, y_pin, connect_pins))
            elif location == "up":
                for i in place_pin:
                    x_pin = self.x_c - math.ceil(self.w/2/self.grid_size) + (i-1) - 0.225
                    y_pin = self.y_c - self.h/2 - 0.25
                    self.pin.append(Pin(x_pin, y_pin, connect_pins))
            elif location == "down":
                for i in place_pin:
                    x_pin = self.x_c - math.ceil(self.w/2/self.grid_size) + (i-1) - 0.225
                    y_pin = self.y_c + self.h / 2 - 0.25
                    self.pin.append(Pin(x_pin, y_pin, connect_pins))
            else:
                print(location, " :string location is not correct")


class Pin:
    pins_connection = []
    location = (0, 0)

    def __init__(self, x, y, pin_mass):
        self.location = (x, y)
        self.pins_connection = pin_mass

    def paint_pin(self, image, grid_size):
        x_pin_start = self.location[0]*grid_size
        y_pin_start = self.location[1]*grid_size
        x_pin_end = (self.location[0] + 0.5) * grid_size
        y_pin_end = (self.location[1] + 0.5) * grid_size
        image.ellipse([x_pin_start, y_pin_start, x_pin_end, y_pin_end], fill=(255, 102, 0), outline="red")


def init_dictionary():
    element_dictionary: dict[str, BoardElement] = {"resistor10Om": BoardElement(0, 0, 11, 4.5, 1),
                                                   "resistor1kOm": BoardElement(0, 0, 11, 4.5, 1),
                                                   "resistor100Om": BoardElement(0, 0, 11, 4.5, 1),
                                                   "resistor1Om": BoardElement(0, 0, 11, 4, 1),
                                                   "capacitor10mkF": BoardElement(0, 0, 4.5, 3.2, 1),
                                                   "capacitor100mkF": BoardElement(0, 0, 3.5, 2.8, 1),
                                                   "capacitor1mkF": BoardElement(0, 0, 2, 1.25, 1),
                                                   "inductance220mkG": BoardElement,
                                                   "inductance10mkG": BoardElement,
                                                   "K176TM2": BoardElement,
                                                   "TPS51200DRCR": BoardElement,
                                                   "CS48505S": BoardElement,
                                                   "ADM3070EARZ": BoardElement,
                                                   "AD790JNZ": BoardElement,
                                                   "CD74HC123E": BoardElement,
                                                   "23LC1024-I/SN": BoardElement,
                                                   "ADUC812BSZ": BoardElement,
                                                   "AD420ARZ-32-REEL": BoardElement}

    element_dictionary["resistor1Om"].spm = [["left", [1, 2, 3], []], ["right", [1], []], ["up", [1], []], ["down", [1], []]]
    element_dictionary["resistor10Om"].spm = [["left", [1, 2, 3], []], ["right", [1], []], ["up", [], []], ["down", [], []]]
    element_dictionary["resistor100Om"].spm = [["left", [1], []], ["right", [1], []], ["up", [], []], ["down", [], []]]
    element_dictionary["resistor1kOm"].spm = [["left", [1], []], ["right", [1], []], ["up", [], []], ["down", [], []]]
    element_dictionary["capacitor10mkF"].spm = [["left", [1], []], ["right", [1], []], ["up", [], []], ["down", [], []]]
    element_dictionary["capacitor1mkF"].spm = [["left", [1], []], ["right", [1], []], ["up", [], []], ["down", [], []]]
    element_dictionary["capacitor100mkF"].spm = [["left", [1], []], ["right", [1], []], ["up", [], []], ["down", [], []]]
    return element_dictionary


if __name__ == '__main__':
    new_board = MainBoard(1000, 1000, 8)
    el_dict = init_dictionary()
    new_board.append_element(el_dict["resistor10Om"], 10, 11)
    new_board.append_element(el_dict["capacitor100mkF"], 20, 20)
    new_board.show_board()
