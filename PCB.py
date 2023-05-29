from PIL import Image, ImageDraw
import math


class LinearFunc:
    """
    LinearFunc - класс для хранения информации о линейных функциях.
    Ввод: два пина(принимающий, отдающий) и параметры линейной функции.
    """
    def __init__(self, in_pin, out_pin, param_a, param_b):
        self.in_pin = in_pin
        self.out_pin = out_pin
        self.a = param_a
        self.b = param_b


class Board:
    """
    Board предназначен для формирования макета печатной платы.
    """
    def __init__(self, user_width, user_height, user_grid):
        """
        В конструктор вводится длина, высота платы, а также размер шага сетки.
        """
        self.width = user_width
        self.height = user_height
        self.gridDivisionSize = user_grid
        self.image = Image.new("RGB", (self.width, self.height), (0, 255, 0))
        self.paint_grid()
        self.elements = []

    def paint_elements(self):
        """
        paint_elements добавляет к визуализации платы рисунки элементов.
        """
        if len(self.elements) != 0:
            for i in self.elements:
                i.paint_element(self.image, self.gridDivisionSize)

    def paint_grid(self):
        """
        paint_grid отвечает за разметку сетки.
        """
        grid = self.gridDivisionSize
        image_grid = ImageDraw.Draw(self.image)
        horizontal_step = math.ceil(self.height/grid)
        vertical_step = math.ceil(self.width/grid)
        for i in range(0, vertical_step+1):
            image_grid.line([(i*grid, 0), (i*grid, self.height)], 1)
        for j in range(0, horizontal_step+1):
            image_grid.line([(0, j*grid), (self.width, j*grid)], 1)

    def append_element(self, inst, x_c, y_c, rotation="", pins=[]):
        """
        append_element добавляет новый элемент, используя макет.
        :param inst: макет элемента.
        :param x_c: абсцисса центра элемента.
        :param y_c: ордината центра элемента.
        :param rotation: поворот влево/вправо.
        :param pins: массив со связанными с элементом пинами.
        """
        element_buf = Component(x_c, y_c, inst[0][0], inst[0][1], self.gridDivisionSize, inst[1], rotation, pins)
        element_buf.append_pins(inst[2])
        self.elements.append(element_buf)

    def show_board(self):
        """
        show_board создает картинку печатной платы, со всеми
        элементами и соединениями.
        :return: Image
        """
        self.paint_elements()
        self.wires_drawing()
        return self.image.copy()

    def separate_in_out_pins(self):
        """
        separate_in_out_pins разделяет пины на входящие и исходящие.
        :return: массив входящих пинов (in_pins), массив исходящих пинов (out_pins).
        """
        in_pins = []
        out_pins = []
        for i in self.elements:
            for j in i.pin:
                if j.connection[1] == "in":
                    in_pins.append(j)
                elif j.connection[1] == "out":
                    out_pins.append(j)
        return in_pins, out_pins

    def wires_drawing(self):
        """
        wires_drawing отрисовывает провода на плате.
        """
        draw_image = ImageDraw.Draw(self.image)
        grid = self.gridDivisionSize
        in_pins, out_pins = self.separate_in_out_pins()
        for i in in_pins:
            for j in out_pins:
                if i.connection[0] == j.connection[0]:
                    x_start = i.location[0]*grid
                    y_start = i.location[1]*grid+2
                    x_end = j.location[0]*grid
                    y_end = j.location[1]*grid+2
                    draw_image.line((x_start, y_start, x_end, y_end), fill="purple", width=1)

    def HPWL(self):
        """
        HPWL функция расчета полупериметра в актуальной конфигурации платы.
        :return: общую длину проводов.
        """
        result = 0
        in_pins, out_pins = self.separate_in_out_pins()
        for i in in_pins:
            for j in out_pins:
                if i.connection[0] == j.connection[0]:
                    result += abs(i.location[0] - j.location[0]) + abs(i.location[1] - j.location[1])
        return result

    def location_density(self):
        """
        location_density рассчитывает плотность размещения элементов.
        :return: плотность размещения.
        """
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
        return element_area/(max_x-min_x)*(max_y-min_y)

    def check_overlays(self):
        """
        check_overlays проверка на перекрытия между элементами.
        :return: количество пересекающихся элементов.
        """
        overlays = 0
        checked = []
        num_elements = len(self.elements)
        for s in range(0, num_elements):
            for z in range(s, num_elements):
                if s == z or z in checked:
                    continue
                else:
                    delta_x = abs(self.elements[s].x_c - self.elements[z].x_c)
                    delta_y = abs(self.elements[s].y_c - self.elements[z].y_c)
                    union_width = (self.elements[s].w + self.elements[z].w)/2
                    union_height = (self.elements[s].h + self.elements[z].h)/2
                    if delta_x == 0 and delta_y == 0:
                        overlays += 2
                        checked.append(z)
                    elif delta_x <= union_width or delta_y <= union_height:
                        overlays += 1
                        checked.append(z)

        return overlays

    def check_wires_overlays(self):
        """
        check_wires_overlays проверяет проводящие дорожки на факт пересечения.
        :return: количество пересечений.
        """
        functions = []
        intersections = 0
        in_pins, out_pins = self.separate_in_out_pins()
        for i in in_pins:
            for j in out_pins:
                x_in_i = i.location[0]
                x_out_i = j.location[0]
                y_in = i.location[1]
                y_out = j.location[1]
                if i.connection[0] == j.connection[0]:
                    if y_in == y_out:
                        a = 0
                    elif x_in_i - x_out_i == 0:
                        a = (y_in - y_out) / 0.00000001
                    else:
                        a = (y_in - y_out) / (x_in_i - x_out_i)
                    b = y_in - a*x_in_i
                    functions.append(LinearFunc(i, j, a, b))
        len_functions = len(functions)
        for s in range(0, len_functions):
            for z in range(s, len_functions):
                if s == z:
                    continue
                i = functions[s]
                j = functions[z]

                x_in_i = i.in_pin.location[0]
                x_out_i = i.out_pin.location[0]
                y_in_i = i.in_pin.location[1]
                y_out_i = i.out_pin.location[1]

                x_in_j = j.in_pin.location[0]
                x_out_j = j.out_pin.location[0]
                y_in_j = j.in_pin.location[1]
                y_out_j = j.out_pin.location[1]
                if i.a == j.a and j.b == i.b and (x_in_i >= x_in_j >= x_out_i or x_out_i >= x_in_j >= x_in_i):
                    intersections += 1
                elif i.a == j.a and j.b != i.b:
                    continue
                else:
                    x_inter = (j.b - i.b)/(i.a - j.a)
                    y_inter = j.a * x_inter + j.b
                    if x_in_i >= x_inter >= x_out_i or x_out_i >= x_inter >= x_in_i:
                        intersections += 1
        functions.clear()
        return intersections

    def check_out_of_bounds(self):
        """
        check_out_of_bounds проверяет элементы на факт выхода за пределы платы.
        :return: количество вышедших за пределы платы элементов.
        """
        outs = 0
        for i in self.elements:
            if i.x_c + i.w/2 > self.width or i.x_c - i.w/2 < 0:
                outs += 1
            if i.y_c + i.h/2 > self.height or i.y_c - i.h/2 < 0:
                outs += 1
        return outs

    def design_error(self):
        """
        design_error создает значение ошибки проектирования платы.
        :return: значение ошибки.
        """
        return self.check_wires_overlays() + self.check_overlays()*5 + self.check_out_of_bounds()*10

    def __del__(self):
        self.elements.clear()


class Component:
    """
    Component класс для описания компонентов печатной платы.
    """
    def __init__(self, x=0, y=0, h=0, w=0, grid_size=0, name='', rotation="", pins=[]):
        """
        В конструкторе вводят параметры размещения и соединения с другими компонентами.
        :param x: абсцисса центра компонента
        :param y: ордината центра компонента
        :param h: длина элемента
        :param w: ширина элемента
        :param grid_size: величина шага сетки
        :param name: название элемента
        :param rotation: поворот влево/вправо
        :param pins: соединения с другими элементами
        """
        self.x_c = x
        self.y_c = y
        self.h = h
        self.w = w
        self.grid = grid_size
        self.name = name
        self.rotation = rotation
        self.pin = []
        self.spm = []
        self.pin_channels = []
        for i in pins:
            self.pin_channels.append(i)

    def recalculate_pins(self):
        """
        recalculate_pins пересчитывает координаты пинов в соотвествии с поворотом элемента.
        """
        new_pins = []
        rotation = self.rotation
        x = self.x_c
        y = self.y_c
        if rotation == "left":
            for i in self.pin:
                location = (x + (i.location[1] - y), y - (i.location[0] - x) - 0.5)
                pins = i.connection
                new_pins.append(Pin(location[0], location[1], pins[0], pins[1]))
        elif rotation == "right":
            for i in self.pin:
                location = (x - (i.location[1] - y) - 0.5, y + (i.location[0] - x))
                pins = i.connection
                new_pins.append(Pin(location[0], location[1], pins[0], pins[1]))
        self.pin = []
        for i in new_pins:
            self.pin.append(Pin(i.location[0], i.location[1], i.connection[0], i.connection[1]))
        new_pins = []

    def paint_element(self, image, grid):
        """
        pain_element функция которая отрисовывает элемент с его пинами на печатной плате.
        :param image: картинка на которой все рисуется.
        :param grid: размер шага сетки.
        """
        image_draw = ImageDraw.Draw(image)
        x = self.x_c
        y = self.y_c
        w = self.w
        h = self.h
        if self.rotation in ["left", "right"]:
            x_start = (x - h/2) * grid
            y_start = (y - w/2) * grid
            x_end = (x + h/2) * grid
            y_end = (y + w/2) * grid
            self.recalculate_pins()
        else:
            x_start = (x - w / 2) * grid
            y_start = (y - h / 2) * grid
            x_end = (x + w / 2) * grid
            y_end = (y + h / 2) * grid
        position = (x_start, y_start, x_end, y_end)
        image_draw.rounded_rectangle(xy=position, radius=1, fill=(255, 255, 0), outline="red")
        for i in self.pin:
            i.paint_pin(image_draw, grid)

    def append_pins(self, locations):
        """
        append_pins добавляет новые пины, с помощью специльного массива.
        :param locations: содержит все необходимые данные для описания пина.
        """
        num = -1
        for i in locations:
            num += 1
            if len(i) != 0:
                if len(self.pin_channels) != 0:
                    self.append(i[0], i[1], self.pin_channels[num], i[3])
                else:
                    self.append(i[0], i[1], [], i[3])

    def append(self, location, place_pin, connection, contact_step):
        """
        append добавляет множество новых пинов сверху, снизу, справа, слева.
        :param location: локации пинов (сверху, снизу, справа, слева).
        :param place_pin: старые координаты пинов.
        :param connection: набор пинов соединенных с рассматриваемым.
        :param contact_step: величина шага между пинами.
        """
        x = self.x_c
        y = self.y_c
        h = self.h
        w = self.w
        x_pin = 0
        y_pin = 0
        num_places = len(place_pin)
        num_pins = len(connection)
        if contact_step == 1:
            h_new = math.floor(h / 2)
            w_new = math.floor(w / 2)
        else:
            h_new = (num_places - 1) * contact_step / 2
            w_new = (num_places - 1) * contact_step / 2
        if num_places != 0:
            for i in range(0, num_places):
                if location == "right":
                    x_pin = x + w / 2 - 0.25
                    y_pin = y - h_new + (place_pin[i] - 1) * contact_step - 0.225
                elif location == "left":
                    x_pin = x - w / 2 - 0.25
                    y_pin = y - h_new + (place_pin[i] - 1) * contact_step - 0.225
                elif location == "up":
                    x_pin = x - w_new + (place_pin[i] - 1) * contact_step - 0.225
                    y_pin = y - h / 2 - 0.25
                elif location == "down":
                    x_pin = x - w_new + (place_pin[i] - 1) * contact_step - 0.225
                    y_pin = y + h / 2 - 0.25
                if num_pins != 0:
                    new_pin = Pin(x_pin, y_pin, connection[i][0], connection[i][1])
                else:
                    new_pin = Pin(x_pin, y_pin)
                self.pin.append(new_pin)


class Pin:
    """
    Pin класс использующийся для описания соединений между элементами.
    """
    def __init__(self, x, y, name="", type_pin=""):
        """
        Конструктор создает новый пин с названием связи и ее типом, также воводятся его координаты.
        :param x: абсцисса пина
        :param y: ордината пина.
        :param connection_name: название соединения.
        :param pin_type: тип пина in/out
        """
        self.location = (x, y)
        self.connection = (name, type_pin)

    def paint_pin(self, image, grid):
        """
        paint_pin отрисовывает пины на плате.
        :param image: картинка платы.
        :param grid: шаг сетки.
        """
        x = self.location[0]
        y = self.location[1]
        x_start = x * grid
        y_start = y * grid
        x_end = (x + 0.5) * grid
        y_end = (y + 0.5) * grid
        image.ellipse([x_start, y_start, x_end, y_end], fill=(255, 102, 0), outline="red")
