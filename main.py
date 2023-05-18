from PIL import Image, ImageShow, ImageDraw
import math


class MainBoard:
    def __init__(self, user_width, user_height, user_grid):
        self.width = user_width
        self.height = user_height
        self.gridDivisionSize = user_grid
        self.image = Image.new("RGB", (self.width, self.height), (0, 255, 0))
        self.paint_grid()
        self.elements = []

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

    def append_new_element(self, x_c, y_c, h, w, name):
        self.elements.append(BoardElement(x_c, y_c, h, w, self.gridDivisionSize, name))

    def append_element(self, instance, x_c, y_c, rotation="", mass_pin_channels=[]):
        element_buf = BoardElement(x_c, y_c, instance.h, instance.w, self.gridDivisionSize,
                                   instance.element_name, rotation, mass_pin_channels)
        element_buf.append_pins(instance.spm)
        self.elements.append(element_buf)

    def show_board(self):
        self.paint_elements()
        self.wires_drawing()
        return self.image.copy()
        #ImageShow.show(self.image, "Board")
    def show_board_special(self):
        self.paint_elements()
        self.wires_drawing()
        ImageShow.show(self.image, "Board")

    def wires_drawing(self):
        draw = ImageDraw.Draw(self.image)
        mass_in_pins = []
        mass_out_pins = []
        for i in self.elements:
            for j in i.pin:
                if j.pins_connection[1] == "in":
                    mass_in_pins.append(j)
                elif j.pins_connection[1] == "out":
                    mass_out_pins.append(j)
        for i in mass_in_pins:
            for j in mass_out_pins:
                if i.pins_connection[0] == j.pins_connection[0]:
                    draw.line((i.location[0]*self.gridDivisionSize+2, i.location[1]*self.gridDivisionSize+2,
                               j.location[0]*self.gridDivisionSize+2, j.location[1]*self.gridDivisionSize+2),
                              fill="purple", width=1)
                    #print((i.location[0], j.location[0], i.location[1], j.location[1]))

    def HPWL(self):
        result_length = 0
        mass_in_pins = []
        mass_out_pins = []
        for i in self.elements:
            for j in i.pin:
                if j.pins_connection[1] == "in":
                    mass_in_pins.append(j)
                elif j.pins_connection[1] == "out":
                    mass_out_pins.append(j)
        for i in mass_in_pins:
            for j in mass_out_pins:
                if i.pins_connection[0] == j.pins_connection[0]:
                    result_length += abs(i.location[0] - j.location[0]) + abs(i.location[1] - j.location[1])
        return result_length

    def location_density(self):
        element_area = 0
        max_x = 0
        min_x = 100000
        max_y = 0
        min_y = 100000
        for i in self.elements:
            if i.x_c + i.w/2 > max_x:
                max_x = i.x_c + i.w/2
            elif i.x_c - i.w/2 < min_x:
                min_x = i.x_c - i.w/2
            if i.y_c + i.h/2 > max_y:
                max_y = i.y_c + i.h/2
            elif i.y_c - i.h/2 < min_y:
                min_y = i.y_c - i.h/2

            element_area += i.h*i.w
        extreme_area = (max_x-min_x)*(max_y-min_y)
        return element_area/extreme_area

    ## Добавить в ошибку обработку выхода части элемента за границу платы
    def design_error(self):
        mass_in_pins = []
        mass_out_pins = []
        for i in self.elements:
            for j in self.elements:
                if j == i:
                    continue
                else:
                    if abs(i.x_c-j.x_c) <= (i.w + j.w)/2:
                        return True
                    if abs(i.y_c-j.y_c) <= (i.h + j.h)/2:
                        return True
            for j in i.pin:
                if j.pins_connection[1] == "in":
                    mass_in_pins.append(j)
                elif j.pins_connection[1] == "out":
                    mass_out_pins.append(j)
        for i in mass_in_pins:
            for j in mass_out_pins:
                if i == j:
                    continue
                if i.pins_connection[0] == j.pins_connection[0]:
                    for z in mass_in_pins:
                        if z == i or z == j:
                            continue
                        for s in mass_out_pins:
                            if s == z or s == i or s == j:
                                continue
                            if z.pins_connection[0] == s.pins_connection[0]:
                                if i.location[0] - z.location[0] < 0 and j.location[0] - s.location[0] < 0 \
                                        or i.location[0] - z.location[0] > 0 and j.location[0] - s.location[0] > 0:
                                    return False
                                elif i.location[0] - s.location[0] < 0 and j.location[0] - z.location[0] < 0 \
                                        or i.location[0] - s.location[0] > 0 and j.location[0] - z.location[0] > 0:
                                    return False
                                else:
                                    return True


class BoardElement:
    def __init__(self, x=0, y=0, h=0, w=0, grid_size=0, name='', rotation="", mass_pin_channels=[]):
        self.x_c = x
        self.y_c = y
        self.h = h
        self.w = w
        self.grid_size = grid_size
        self.element_name = name
        self.rotation = rotation
        self.pin = []
        self.spm = []
        self.pin_channels = []
        for i in mass_pin_channels:
            self.pin_channels.append(i)

    def recalculate_pins(self):
        new_pins = []
        if self.rotation == "left":
            for i in self.pin:
                location = (self.x_c + math.cos(math.pi / 2) * (i.location[0] - self.x_c) + math.sin(math.pi / 2) *
                            (i.location[1] - self.y_c),
                            self.y_c - math.sin(math.pi / 2) *
                            (i.location[0] - self.x_c) + math.cos(math.pi / 2) * (i.location[1] - self.y_c) - 0.5)

                pin_mass = i.pins_connection
                new_pins.append(Pin(location[0], location[1], pin_mass[0], pin_mass[1]))
        elif self.rotation == "right":
            for i in self.pin:
                location = (self.x_c + math.cos(math.pi / 2) * (i.location[0] - self.x_c) - math.sin(math.pi / 2) *
                            (i.location[1] - self.y_c),
                            self.y_c + math.sin(math.pi / 2) *
                            (i.location[0] - self.x_c) + math.cos(math.pi / 2) * (i.location[1] - self.y_c))
                pin_mass = i.pins_connection
                new_pins.append(Pin(location[0], location[1], pin_mass[0], pin_mass[1]))
        self.pin = []
        for i in new_pins:
            self.pin.append(Pin(i.location[0], i.location[1], i.pins_connection[0], i.pins_connection[1]))
        new_pins.clear()

    def paint_element(self, image, grid_size):
        image_print_element = ImageDraw.Draw(image)
        if self.rotation in ["left", "right"]:
            x_low_pos = (self.x_c - self.h/2)*grid_size
            y_low_pos = (self.y_c - self.w/2)*grid_size
            x_high_pos = (self.x_c + self.h/2)*grid_size
            y_high_pos = (self.y_c + self.w/2)*grid_size
            self.recalculate_pins()

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
        counter = -1
        for i in locations_places:
            counter += 1
            if len(i) != 0:
                if len(self.pin_channels) != 0:
                    self.append_new_pin(i[0], i[1], self.pin_channels[counter], i[3])
                else:
                    self.append_new_pin(i[0], i[1], [], i[3])

    def append_new_pin(self, location, place_pin, connect_pins, step_size_contact):
        try:
            if step_size_contact == 1:
                h_new = math.floor(self.h*self.grid_size/(2*self.grid_size))
                w_new = math.floor(self.w*self.grid_size/(2*self.grid_size))
            else:
                indent_h = (self.h - (len(place_pin) - 1) * step_size_contact)/2
                indent_w = (self.w - (len(place_pin) - 1) * step_size_contact)/2
                h_new = self.h/2 - indent_h
                w_new = self.w/2 - indent_w
            if len(place_pin) != 0:
                if location == "right":
                    for i in range(0, len(place_pin)):
                        x_pin = self.x_c + self.w/2 - 0.25
                        y_pin = self.y_c - h_new + (place_pin[i]-1)*step_size_contact - 0.225
                        if len(connect_pins) != 0:
                            new_pin = Pin(x_pin, y_pin, connect_pins[i][0], connect_pins[i][1])
                        else:
                            new_pin = Pin(x_pin, y_pin)
                        self.pin.append(new_pin)
                elif location == "left":
                    for i in range(0, len(place_pin)):
                        x_pin = self.x_c - self.w/2 - 0.25
                        y_pin = self.y_c - h_new + (place_pin[i]-1)*step_size_contact - 0.225
                        if len(connect_pins) != 0:
                            new_pin = Pin(x_pin, y_pin, connect_pins[i][0], connect_pins[i][1])
                        else:
                            new_pin = Pin(x_pin, y_pin)
                        self.pin.append(new_pin)
                elif location == "up":
                    for i in range(0, len(place_pin)):
                        x_pin = self.x_c - w_new + (place_pin[i]-1)*step_size_contact - 0.225
                        y_pin = self.y_c - self.h/2 - 0.25
                        if len(connect_pins) != 0:
                            new_pin = Pin(x_pin, y_pin, connect_pins[i][0], connect_pins[i][1])
                        else:
                            new_pin = Pin(x_pin, y_pin)
                        self.pin.append(new_pin)
                elif location == "down":
                    for i in range(0, len(place_pin)):
                        x_pin = self.x_c - w_new + (place_pin[i]-1)*step_size_contact - 0.225
                        y_pin = self.y_c + self.h / 2 - 0.25
                        if len(connect_pins) != 0:
                            new_pin = Pin(x_pin, y_pin, connect_pins[i][0], connect_pins[i][1])
                        else:
                            new_pin = Pin(x_pin, y_pin)
                        self.pin.append(new_pin)
                else:
                    print(location, " :string location is not correct")
        except:
            print("НЕ ВСЕ ДАННЫЕ О ПИНАХ ВВЕДЕНЫ!!!")


class Pin:

    def __init__(self, x, y, connection_name="", exit_input=""):
        self.location = (x, y)
        self.pins_connection = (connection_name, exit_input)

    def paint_pin(self, image, grid_size):                      # Потом добавить названия connection_name на схему
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
                                                   "AD420ARZ-32-REEL": BoardElement(0, 0, 15.2, 7.6, 1, "AD420ARZ-32-REEL"),
                                                   "ground": BoardElement(0, 0, 1, 1, 1, "ground")}

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
    element_dictionary["ground"].spm = [[], [], ["up", [1], [], 1], []]
    return element_dictionary