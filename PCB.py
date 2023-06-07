from PIL import Image, ImageDraw, ImageShow
import math
from numpy import sign
import random


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

    def copy(self):
        copy_board = Board(self.width, self.height, self.gridDivisionSize)
        copy_board.elements = self.elements.copy()
        return copy_board

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

    def show_board(self, trase_on=False):
        """
        show_board создает картинку печатной платы, со всеми
        элементами и соединениями.
        :return: Image
        """
        self.paint_elements()
        self.wires_drawing(trase_on)
        return self.image.copy()

    def separate_in_out_pins(self):
        """
        separate_in_out_pins разделяет пины на входящие и исходящие.
        :return: массив входящих пинов (in_pins), массив исходящих пинов (out_pins).
        """
        in_pins = []
        out_pins = []
        for i in self.elements:
            for j in i.pins:
                if j.connection[1] == "in":
                    in_pins.append(j)
                elif j.connection[1] == "out":
                    out_pins.append(j)
        return in_pins, out_pins

    def wires_drawing(self, trase_on = False):
        """
        wires_drawing отрисовывает провода на плате.
        """
        draw_image = ImageDraw.Draw(self.image)
        grid = self.gridDivisionSize
        in_pins, out_pins = self.separate_in_out_pins()
        counter = 0
        mass_deltas = []
        for i in in_pins:
            for j in out_pins:
                if i.connection[0] == j.connection[0]:
                    x_start = i.location[0]*grid
                    y_start = i.location[1]*grid+2
                    x_end = j.location[0]*grid
                    y_end = j.location[1]*grid+2
                    if trase_on:
                        self.trase([i, j], mass_deltas)
                    else:
                        draw_image.line((x_start, y_start, x_end, y_end), fill="purple", width=1)
                    draw_image.text((x_start, y_start), text=i.connection[0], fill=(255, 255, 255))
                    draw_image.text((x_end, y_end), text=j.connection[0], fill=(255, 255, 255))
                    counter += 1

    def init_trase(self, location, friend, draw_image, width):
        for i in self.elements:
            minus_delta_y = i.y_c - i.h/2 - 0.25
            plus_delta_y = i.y_c + i.h/2 - 0.25
            minus_delta_x = i.x_c - i.w/2 - 0.25
            plus_delta_x = i.x_c + i.w/2 - 0.25
            grid = self.gridDivisionSize
            x = -1
            y = -1
            new_x = -1
            new_y = -1
            if plus_delta_x == location[0] and plus_delta_y >= location[1] >= minus_delta_y:
                # right
                x = (location[0] + 0.5)
                y = (location[1] + 0.25)
                new_x = math.ceil(location[0] + 0.5)
                new_y = y
                draw_image.line((x*grid, y*grid, new_x*grid, new_y*grid), fill="purple", width=width)
                if location[1] > friend[1]:
                    draw_image.line((new_x * grid, new_y * grid, new_x * grid, math.floor(location[1] + 0.25) * grid),
                                    fill="purple", width=width)
                    return False, (new_x, math.floor(location[1] + 0.25))
                else:
                    draw_image.line((new_x * grid, new_y * grid, new_x * grid,  math.ceil(location[1] + 0.25) * grid),
                                    fill="purple", width=width)
                    return False, (new_x, math.ceil(location[1] + 0.25))
            elif minus_delta_x == location[0] and plus_delta_y >= location[1] >= minus_delta_y:
                # left
                x = location[0]
                y = (location[1] + 0.25)
                new_x = math.floor(location[0])
                new_y = y
                draw_image.line((x*grid, y*grid, new_x*grid, new_y*grid), fill="purple", width=width)
                if location[1] > friend[1]:
                    draw_image.line((new_x * grid, new_y * grid, new_x * grid, math.floor(location[1] + 0.25) * grid),
                                    fill="purple", width=width)
                    return False, (new_x, math.floor(location[1] + 0.25))
                else:
                    draw_image.line((new_x * grid, new_y * grid, new_x * grid, math.ceil(location[1] + 0.25)*grid),
                                    fill="purple", width=width)
                    return False, (new_x, math.ceil(location[1] + 0.25))
            elif plus_delta_y == location[1] and plus_delta_x >= location[0] >= minus_delta_x:
                # down
                x = (location[0] + 0.25)
                y = (location[1] + 0.5)
                new_x = x
                new_y = math.ceil(location[1] + 0.5)
                draw_image.line((x*grid, y*grid, new_x*grid, new_y*grid), fill="purple", width=width)
                if location[0] > friend[0]:
                    draw_image.line((new_x * grid, new_y * grid, math.floor(location[0] + 0.25) * grid, new_y * grid),fill="purple", width=width)
                    return False, (math.floor(location[0] + 0.25), new_y)
                else:
                    draw_image.line((new_x * grid, new_y * grid, math.ceil(location[0] + 0.25) * grid, new_y * grid),fill="purple", width=width)
                    return False, (math.ceil(location[0] + 0.25), new_y)
            elif minus_delta_y == location[1] and plus_delta_x >= location[0] >= minus_delta_x:
                # up
                x = (location[0] + 0.25)
                y = location[1]
                new_x = x
                new_y = math.floor(location[1])
                draw_image.line((x*grid, y*grid, new_x*grid, new_y*grid), fill="purple", width=width)
                if location[0] > friend[0]:
                    draw_image.line((new_x * grid, new_y * grid, math.floor(location[0] + 0.25) * grid, new_y * grid),
                                    fill="purple", width=width)
                    return False, (math.floor(location[0] + 0.25), new_y)
                else:
                    draw_image.line((new_x * grid, new_y * grid, math.ceil(location[0] + 0.25) * grid, new_y * grid),
                                    fill="purple", width=width)
                    return False, (math.ceil(location[0] + 0.25), new_y)
        return True, (round(new_x), round(new_y))

    def check_wires_elements(self, start):
        x = start[0]
        y = start[1]
        grid = self.gridDivisionSize
        if x <= 0 or x >= self.width/grid or y <= 0 or y >= self.height/grid:
            print("No Bound")
            x_new = 0
            y_new = 0
            if x <= 0:
                x_new = 1 - x
            elif x >= self.width/grid:
                x_new = x - self.width/grid + 1
            if y <= 0:
                y_new = 1 - y
            elif y >= self.height/grid:
                y_new = y - self.height/grid + 1
            return True, (-math.floor(x_new), -math.floor(y_new))
        for i in self.elements:
            x_new = 0
            y_new = 0
            minus_delta_y = math.floor(i.y_c * grid - i.h * grid / 2)/grid
            plus_delta_y = math.ceil(i.y_c * grid + i.h * grid / 2)/grid
            minus_delta_x = math.floor(i.x_c * grid - i.w * grid / 2)/grid
            plus_delta_x = math.ceil(i.x_c * grid + i.w * grid / 2)/grid
            if plus_delta_x >= x >= minus_delta_x and plus_delta_y >= y >= minus_delta_y:
                if plus_delta_x - x >= x - minus_delta_x:
                    x_new = -math.floor(x - minus_delta_x + 1)
                else:
                    x_new = math.floor(plus_delta_x - x + 1)
                if plus_delta_y - y >= y - minus_delta_y:
                    y_new = -math.floor(y - minus_delta_y + 1)
                else:
                    y_new = math.floor(plus_delta_y - y + 1)
                print("Check!!! start:", start, "(width,height):", self.width/grid, self.height/grid, "widthEL:", plus_delta_x,
                      minus_delta_x, "heightEL:", plus_delta_y, minus_delta_y, "diff:", x_new, y_new)
                return True, (x_new, y_new)
        return False, (0, 0)

    def trase(self, pins, mass_deltas):
        start = pins[0].location
        end = pins[1].location
        draw_image = ImageDraw.Draw(self.image)
        big_flag = True
        flag_x = False
        grid = self.gridDivisionSize
        path = []
        error, start = self.init_trase(start, end, draw_image, 2)
        if error:
            print("InitTrase Error! Pin name:", pins[0].connection[0])
        error, end = self.init_trase(end, start, draw_image, 2)
        if error:
            print("InitTrase Error! Pin name:", pins[1].connection[0])

        while big_flag:
            print("start:", start, "end:", end)
            if start[0] - end[0] == 0 and start[1] - end[1] == 0:
                big_flag = False
                break
            else:
                sign_x = sign(start[0] - end[0])
                difference = int(abs(start[0] - end[0]))
                print("difference:", difference)
                buffer = start
                for x in range(0, difference + 1):
                    print(x, " start:", start)
                    if abs(start[0] - end[0]) == 0:
                        break
                    flag_error, new_diff = self.check_wires_elements(start)
                    print(new_diff)
                    if flag_error:
                        x_old = start[0] * grid
                        y_old = start[1] * grid
                        start = (start[0] + new_diff[0], start[1] + new_diff[1])
                        x_new = start[0] * grid
                        y_new = start[1] * grid
                        #path.append([x_new, y_new])
                        flag_x = True
                        #draw_image.line((x_old, y_old, x_new, y_new), fill="purple")
                        break
                    else:
                        buffer = start
                        start = (start[0] - sign_x * 1, start[1])
                        x_old = (start[0] + sign_x * 1) * grid
                        x_new = start[0] * grid
                        y_new = start[1] * grid
                        y_old = start[1] * grid
                        if len(path)!=0:
                            if x_old - path[len(path)-1][0] != 0 and y_old - path[len(path)-1][1] != 0:
                                path.append([path[len(path)-1][0], y_old])
                        path.append([x_old, y_old])
                        #draw_image.line((x_old, y_old, x_new, y_new), fill="purple")
                if flag_x:
                    flag_x = False
                    continue
                sign_y = sign(start[1] - end[1])
                difference = abs(start[1] - end[1])
                for y in range(0, difference + 1):
                    print(y, " start:", start, )
                    if abs(start[1] - end[1]) == 0 and abs(start[0] - end[0]) == 0:
                        path.append([start[0]*grid, start[1]*grid])
                        break
                    flag_error, new_diff = self.check_wires_elements(start)
                    if flag_error:
                        x_old = start[0] * grid
                        y_old = start[1] * grid
                        start = (start[0] + new_diff[0], start[1] + new_diff[1])
                        x_new = start[0] * grid
                        y_new = start[1] * grid
                        #path.append([x_new, y_new])
                        #draw_image.line((x_old, y_old, x_new, y_new), fill="purple")
                    else:
                        buffer = start
                        start = (start[0], start[1] - sign_y * 1)
                        x_old = start[0] * grid
                        x_new = start[0] * grid
                        y_new = start[1] * grid
                        y_old = (start[1] + sign_y * 1) * grid
                        if len(path) != 0:
                            if x_old - path[len(path) - 1][0] != 0 and y_old - path[len(path) - 1][1] != 0:
                                path.append([path[len(path) - 1][0], y_old])
                        path.append([x_old, y_old])
                        #draw_image.line((x_old, y_old, x_new, y_new), fill="purple")
        print(path)
        for i in range(1, len(path)):
            draw_image.line((path[i-1][0], path[i-1][1], path[i][0], path[i][1]), fill="purple", width=2)

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
        max_x = -0.5
        min_x = 1000000
        max_y = -0.5
        min_y = 1000000
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
        return element_area/((max_x-min_x)*(max_y-min_y))

    def check_overlays(self):
        """
        check_overlays проверка на перекрытия между элементами.
        :return: количество пересекающихся элементов.
        """
        overlays = 0
        checked = []
        for s in range(0, len(self.elements)):
            for z in range(s, len(self.elements)):
                if self.elements[s] != self.elements[z] and (self.elements[z] not in checked or self.elements[s] not in checked):
                    delta_x = abs(self.elements[s].x_c - self.elements[z].x_c)
                    delta_y = abs(self.elements[s].y_c - self.elements[z].y_c)
                    union_width = (self.elements[s].w + self.elements[z].w)/2
                    union_height = (self.elements[s].h + self.elements[z].h)/2
                    if delta_x == 0 and delta_y == 0 or delta_x == 0 and delta_y <= union_height or \
                            delta_x <= union_width and delta_y == 0 or \
                            delta_x <= union_width and delta_y <= union_height:
                        overlays += 1
                        checked.append(self.elements[z])
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
                    if y_in_i >= y_in_j >= y_out_i or y_out_i >= y_in_j >= y_in_i:
                        intersections += 1
                else:
                    if i.a - j.a != 0:
                        x_inter = (j.b - i.b)/(i.a - j.a)
                        y_inter = j.a * x_inter + j.b
                        if (x_in_i >= x_inter >= x_out_i or x_out_i >= x_inter >= x_in_i) and (x_in_j >= x_inter >= x_out_j or x_out_j >= x_inter >= x_in_j):
                            if (y_in_i >= y_inter >= y_out_i or y_out_i >= y_inter >= y_in_i) and (y_in_j >= y_inter >= y_out_j or y_out_j >= y_inter >= y_in_j):
                                intersections += 1
        functions.clear()
        return intersections

    def check_out_of_bounds(self):
        """
        check_out_of_bounds проверяет элементы на факт выхода за пределы платы.
        :return: количество вышедших за пределы платы элементов.
        """
        outs = 0
        w_board = self.width
        h_board = self.height
        grid = self.gridDivisionSize
        for i in self.elements:
            if i.x_c + i.w/2 >= math.floor(w_board/grid) or i.x_c - i.w/2 <= 0:
                outs += 1
            if i.y_c + i.h/2 >= math.floor(h_board/grid) or i.y_c - i.h/2 <= 0:
                outs += 1
        return outs

    def design_error(self):
        """
        design_error создает значение ошибки проектирования платы.
        :return: значение ошибки.
        """
        result = self.check_wires_overlays() + self.check_overlays() + self.check_out_of_bounds()
        return result

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
        self.pins = []
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
            for i in self.pins:
                x_new = i.location[0]
                y_new = i.location[1]
                location = (x + (y_new - y), y - (x_new - x) - 0.5)
                pins = i.connection
                new_pins.append(Pin(location[0], location[1], pins[0], pins[1]))
        elif rotation == "right":
            for i in self.pins:
                x_new = i.location[0]
                y_new = i.location[1]
                location = (x - (y_new - y) - 0.5, y + (x_new - x))
                pins = i.connection
                new_pins.append(Pin(location[0], location[1], pins[0], pins[1]))
        self.pins = []
        for i in new_pins:
            x_new = i.location[0]
            y_new = i.location[1]
            self.pins.append(Pin(x_new, y_new, i.connection[0], i.connection[1]))
        buffer = self.h
        self.h = self.w
        self.w = buffer

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
        for i in self.pins:
            i.paint_pin(image_draw, grid)

    def append_pins(self, locations):
        """
        append_pins добавляет новые пины, с помощью специльного массива.
        :param locations: содержит все необходимые данные для описания пина.
        """
        num = -1
        self.pins.clear()
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
                self.pins.append(new_pin)


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
        #if self.connection[1] != "":
        #    image.text((x_start, y_start), text=self.connection[0], fill=(255, 255, 255))
