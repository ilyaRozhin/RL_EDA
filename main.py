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

    def append_new_element(self, x_c, y_c, h, w, name):
        self.elements.append(BoardElement(x_c, y_c, h, w, self.gridDivisionSize, name))

    def append_element(self, instance, x_c, y_c, rotation=""):
        element_buf = BoardElement(x_c, y_c, instance.h, instance.w, self.gridDivisionSize,
                                   instance.element_name, rotation)
        element_buf.append_pins(instance.spm)
        self.elements.append(element_buf)

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
    element_name = ""
    rotation = ""

    def __init__(self, x, y, h, w, grid_size, name, rotation=""):
        self.x_c = x
        self.y_c = y
        self.h = h
        self.w = w
        self.grid_size = grid_size
        self.element_name = name
        self.rotation = rotation

    def recalculate_pins(self):
        new_pins = []
        if self.rotation == "left":
            for i in self.pin:
                #print("**********")
                #print(i.location)
                #print(self.x_c, self.y_c)
                location = (self.x_c + math.cos(math.pi / 2) * (i.location[0] - self.x_c) + math.sin(math.pi / 2) *
                            (i.location[1] - self.y_c), self.y_c - math.sin(math.pi / 2) *
                            (i.location[0] - self.x_c) + math.cos(math.pi / 2) * (i.location[1] - self.y_c))
                #print(location)
                pin_mass = i.pins_connection
                self.pin.remove(i)
                new_pins.append(Pin(location[0], location[1], pin_mass))
        elif self.rotation == "right":
            for i in self.pin:
                location = (self.x_c + math.cos(math.pi / 2) * (i.location[0] - self.x_c) - math.sin(math.pi / 2) *
                              (i.location[1] - self.y_c), self.y_c + math.sin(math.pi / 2) *
                              (i.location[0] - self.x_c) + math.cos(math.pi / 2) * (i.location[1] - self.y_c))
                pin_mass = i.pins_connection
                self.pin.remove(i)
                #print(self.pin)
                self.pin.append(Pin(location[0], location[1], pin_mass))
        for i in new_pins:
            self.pin.append(Pin(i.location[0], i.location[1], i.pins_connection))
        new_pins.clear()
    def paint_element(self, image, grid_size):
        image_print_element = ImageDraw.Draw(image)
        if self.rotation in ["left", "right"]:
            x_low_pos = (self.x_c - self.h/2)*grid_size
            y_low_pos = (self.y_c - self.w/2)*grid_size
            x_high_pos = (self.x_c + self.h/2)*grid_size
            y_high_pos = (self.y_c + self.w/2)*grid_size
            self.recalculate_pins()
            print([i.location for i in self.pin])
        else:
            x_low_pos = (self.x_c - self.w / 2) * grid_size
            y_low_pos = (self.y_c - self.h / 2) * grid_size
            x_high_pos = (self.x_c + self.w / 2) * grid_size
            y_high_pos = (self.y_c + self.h / 2) * grid_size
        element_position = (x_low_pos, y_low_pos, x_high_pos, y_high_pos)
        image_print_element.rounded_rectangle(xy=element_position, radius=2, fill=(255, 255, 0), outline="red")
        for i in self.pin:
            i.paint_pin(image_print_element, grid_size)

    def append_pins(self, locations_places):
        for i in locations_places:
           if len(i) != 0:
               self.append_new_pin(i[0], i[1], i[2], i[3])

    def append_new_pin(self, location, place_pin, connect_pins, step_size_contact):
        if step_size_contact == 1:
            h_new = math.floor(self.h*self.grid_size/(2*self.grid_size))
            w_new = math.floor(self.w*self.grid_size/(2*self.grid_size))
        else:
            indent_h = (self.h - (len(place_pin)-1) * step_size_contact) / 2
            indent_w = (self.w - (len(place_pin) - 1) * step_size_contact) / 2
            h_new = self.h/2 - indent_h
            w_new = self.w/2 - indent_w
        if len(place_pin) != 0:
            if location == "right":
                for i in place_pin:
                    x_pin = self.x_c + self.w/2 - 0.25
                    y_pin = self.y_c - h_new + (i-1)*step_size_contact - 0.225
                    new_pin = Pin(x_pin, y_pin, connect_pins)
                    self.pin.append(new_pin)
            elif location == "left":
                for i in place_pin:
                    x_pin = self.x_c - self.w/2 - 0.25
                    y_pin = self.y_c - h_new + (i-1)*step_size_contact - 0.225
                    new_pin = Pin(x_pin, y_pin, connect_pins)
                    self.pin.append(new_pin)
                    #print(new_pin)
            elif location == "up":
                for i in place_pin:
                    x_pin = self.x_c - w_new + (i-1)*step_size_contact - 0.225
                    y_pin = self.y_c - self.h/2 - 0.25
                    new_pin = Pin(x_pin, y_pin, connect_pins)
                    self.pin.append(new_pin)
            elif location == "down":
                for i in place_pin:
                    x_pin = self.x_c - w_new + (i-1)*step_size_contact - 0.225
                    y_pin = self.y_c + self.h / 2 - 0.25
                    new_pin = Pin(x_pin, y_pin, connect_pins)
                    self.pin.append(new_pin)
            else:
                print(location, " :string location is not correct")


class Pin:
    pins_connection = []
    location = (0, 0)
    diligent_light = ""

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
    element_dictionary: dict[str, BoardElement] = {"resistor10Om": BoardElement(0, 0, 11, 4.5, 1, "resistor10Om"),
                                                   "resistor1kOm": BoardElement(0, 0, 11, 4.5, 1, "resistor1kOm"),
                                                   "resistor100Om": BoardElement(0, 0, 11, 4.5, 1, "resistor100Om"),
                                                   "resistor1Om": BoardElement(0, 0, 11, 4, 1, "resistor1Om"),
                                                   "capacitor10mkF": BoardElement(0, 0, 4.5, 3.2, 1, "capacitor10mkF"),
                                                   "capacitor100mkF": BoardElement(0, 0, 3.5, 2.8, 1, "capacitor100mkF"),
                                                   "capacitor1mkF": BoardElement(0, 0, 2, 1.25, 1, "capacitor1mkF"),
                                                   "inductance220mkG": BoardElement(0, 0, 12, 7.5, 1, "inductance220mkG"),
                                                   "inductance10mkG": BoardElement(0, 0, 3.2, 1.8, 1, "inductance10mkG"),
                                                   "K176TM2": BoardElement(0, 0, 19.5, 6.6, 1, "K176TM2"),
                                                   "TPS51200DRCR": BoardElement(0, 0, 3, 3, 1, "TPS51200DRCR"),
                                                   "CS48505S": BoardElement(0, 0, 4.9, 3.9, 1, "CS48505S"),
                                                   "ADM3070EARZ": BoardElement(0, 0, 8.5, 6, 1, "ADM3070EARZ"),
                                                   "AD790JNZ": BoardElement(0, 0, 9.4, 6.2, 1, "AD790JNZ"), #
                                                   "CD74HC123E": BoardElement(0, 0, 19.45, 6.6, 1, "CD74HC123E"),
                                                   "23LC1024-I/SN": BoardElement(0, 0, 4.9, 3.9, 1, "23LC1024-I/SN"),
                                                   "ADUC812BSZ": BoardElement(0, 0, 16, 16, 1, "ADUC812BSZ"),
                                                   "AD420ARZ-32-REEL": BoardElement(0, 0, 15.2, 7.6, 1, "AD420ARZ-32-REEL")}

    element_dictionary["resistor1Om"].spm = [[], [], ["up", [3], [], 1], ["down", [3], [], 1]]
    element_dictionary["resistor10Om"].spm = [[], [], ["up", [3], [], 1], ["down", [3], [], 1]]
    element_dictionary["resistor100Om"].spm = [[], [], ["up", [3], [], 1], ["down", [3], [], 1]]
    element_dictionary["resistor1kOm"].spm = [[], [], ["up", [3], [], 1], ["down", [3], [], 1]]
    element_dictionary["capacitor10mkF"].spm = [[], [], ["up", [3], [], 1], ["down", [3], [], 1]]
    element_dictionary["capacitor1mkF"].spm = [[], [], ["up", [3], [], 1], ["down", [3], [], 1]]
    element_dictionary["capacitor100mkF"].spm = [[], [], ["up", [2], [], 1], ["down", [2], [], 1]]
    element_dictionary["inductance220mkG"].spm = [[], [], ["up", [3], [], 1], ["down", [3], [], 1]]
    element_dictionary["inductance10mkG"].spm = [[], [], ["up", [1], [], 1], ["down", [1], [], 1]]
    element_dictionary["K176TM2"].spm = [["left", [1, 2, 3, 4, 5, 6, 7], [], 2.5],
                                         ["right", [1, 2, 3, 4, 5, 6, 7], [], 2.5],
                                         [], []]
    element_dictionary["TPS51200DRCR"].spm = [["left", [1, 2, 3, 4, 5], [], 0.5],
                                              ["right", [1, 2, 3, 4, 5], [], 0.5], [], []]
    element_dictionary["CS48505S"].spm = [["left", [1, 2, 3, 4], [], 1.27], ["right", [1, 2, 3, 4], [], 1.27], [], []]
    element_dictionary["ADM3070EARZ"].spm = [["left", [1, 2, 3, 4, 5, 6, 7], [], 1.27],
                                             ["right", [1, 2, 3, 4, 5, 6, 7], [], 1.27], [], []]
    element_dictionary["AD790JNZ"].spm = [["left", [1, 2, 3, 4], [], 2.54], ["right", [1, 2, 3, 4], [], 2.54], [], []]
    element_dictionary["CD74HC123E"].spm = [["left", [1, 2, 3, 4, 5, 6, 7, 8], [], 2.54],
                                            ["right", [1, 2, 3, 4, 5, 6, 7, 8], [], 2.54], [], []]
    element_dictionary["23LC1024-I/SN"].spm = [["left", [1, 2, 3, 4], [], 1.27],
                                               ["right", [1, 2, 3, 4], [], 1.27], [], []]
    element_dictionary["ADUC812BSZ"].spm = [["left", [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13], [], 0.9],
                                            ["right", [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13], [], 0.9],
                                            ["up", [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13], [], 0.9],
                                            ["down", [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13], [], 0.9]]
    element_dictionary["AD420ARZ-32-REEL"].spm = [["left", [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], [], 1.27],
                                            ["right", [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], [], 1.27], [], []]
    return element_dictionary


if __name__ == '__main__':
    new_board = MainBoard(400, 400, 8)
    el_dict = init_dictionary()
    new_board.append_element(el_dict["K176TM2"], 20, 20)
    new_board.append_element(el_dict["ADUC812BSZ"], 40, 30)
    new_board.append_element(el_dict["resistor1Om"], 10, 10)
    new_board.append_element(el_dict["CD74HC123E"], 10, 40, "left")
    print(len(new_board.elements[0].pin))
    #new_board.append_element(el_dict["resistor1Om"], 80, 80, "left")
    print(len(new_board.elements[0].pin))
    # Разобраться с поворотами
    # Начать что-то делать с проводами
    # Ввести названия на элементах
    new_board.show_board()
