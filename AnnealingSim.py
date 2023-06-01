from PCB import Board
import random
import math
import Config
import matplotlib.pyplot as plt
from datetime import datetime
from PIL import ImageShow
import sys


def gibbs_distribution(temperature, delta_energy):
    """
    gibbs_distribution - функция для расчета распределения Гиббса.
    """
    return math.exp(delta_energy/temperature)


class FullState:
    """
    FullState описывает состояние платы, в котором она находится при использовании Алгоритма Имитации Отжига.
    """
    def __init__(self, alpha, beta, board, config):
        """
        Конструктор формирует начальное состояние платы.
        """
        self.energy = 0
        self.alpha = alpha
        self.beta = beta
        self.last_state = board
        self.images = []
        self.config = [s for s in config]
        self.init_task()
        self.function_energy()

    def init_task(self):
        """
        init_task - инициализирует плату с элементами.
        """
        locations = []
        num_elements = len(self.config)
        x_max = math.floor(self.last_state.width/self.last_state.gridDivisionSize)
        y_max = math.floor(self.last_state.height/self.last_state.gridDivisionSize)
        for s in range(0, num_elements):
            x = random.randint(0, x_max)
            y = random.randint(0, y_max)
            locations.append([x, y])
        self.rebuild_board(locations)
        self.image_state()
        ImageShow.show(self.images[0])

    def image_state(self):
        """
        image_state - сохраняет акутальную картинку платы.
        """
        self.images.append(self.last_state.show_board())

    def rebuild_board(self, locations):
        """
        rebuild_board - пересобирает плату, после предпринятого действия.
        """
        h = self.last_state.height
        w = self.last_state.width
        grid = self.last_state.gridDivisionSize
        len_conf = len(locations)
        self.last_state = Board(w, h, grid)
        for s in range(0, len_conf):
            element = self.config[s][0]
            x = locations[s][0]
            y = locations[s][1]
            rotation = self.config[s][3]
            requirements = self.config[s][4]
            self.last_state.append_element(element, x, y, rotation, requirements)

    def function_energy(self):
        """
        function_energy рассчитывает энерегию с помощью введенной ранее оценочной функции.
        """
        hpwl = self.last_state.HPWL()
        error = self.last_state.design_error()
        if hpwl == 0:
            self.energy = -100
        else:
            self.energy = self.alpha / hpwl + self.beta * self.last_state.location_density() - 10 * error
        if error == 0:
            self.energy *= 10

    def new_full_state(self):
        """
        new_full_state обновляет состояние платы.
        """
        locations = []
        if len(self.images):
            self.images.clear()
        num_elements = len(self.last_state.elements)
        x_max = math.floor(self.last_state.width/self.last_state.gridDivisionSize)
        y_max = math.floor(self.last_state.height/self.last_state.gridDivisionSize)
        for s in range(0, num_elements):
            x = random.randint(0, x_max)
            y = random.randint(0, y_max)
            locations.append([x, y])
        self.rebuild_board(locations)
        self.image_state()

    def transition_to_new_state(self, temperature):
        """
        transition_to_new_state используется для перехода в новое состояние в соответствии с правилами алгоритма имитации отжига.
        """
        old_state = self.last_state.copy()
        old_image = self.images[0]
        old_energy = self.energy
        self.new_full_state()
        self.function_energy()
        if self.energy < old_energy:
            print("Params:", temperature, self.energy - old_energy,
                  gibbs_distribution(temperature, self.energy - old_energy))
            if random.random() > gibbs_distribution(temperature, self.energy - old_energy):
                self.last_state = old_state.copy()
                self.energy = old_energy
                self.images[0] = old_image


def simulation(alpha, beta, count_iter, start_temperature, config_name, h_board, w_board, grid_size, flag_bench=False):
    """
    simulation основная функция алгоритма, запускает симуляцию процесса.
    """
    start = datetime.now()
    dict_conf = Config.init_configuration_dict()
    step = start_temperature/count_iter
    new_board = Board(h_board, w_board, grid_size)
    actual_state = FullState(alpha, beta, new_board, dict_conf[config_name])
    actual_state.images[0].save("results/Annealing_StartImage_" + config_name + ".png")
    max_energy = -10000
    max_images = []
    energy_mass = []
    temperatures = []
    for i in range(0, count_iter-1):
        print("*************", i, "*************")
        print("Old_energy:", actual_state.energy)
        actual_state.transition_to_new_state(start_temperature - i*step)
        print("New_energy:", actual_state.energy)
        if actual_state.energy > 0 and actual_state.energy > max_energy:
            max_energy = actual_state.energy
            max_images.clear()
            max_images.append(actual_state.images[0])
        energy_mass.append(actual_state.energy)
        temperatures.append(start_temperature - i*step)
    print("*******************************")
    print(max_energy)
    if len(max_images):
        max_images[0].save("results/Annealing_MaxImage_" + config_name + ".png")
    temperatures.reverse()
    if flag_bench:
        plt.plot(temperatures, energy_mass)
        plt.title("Values of Energy")
        plt.xlabel("Temperature")
        plt.ylabel("Energy")
        plt.savefig("results/Annealing_" + config_name + "_values_of_energy.png", dpi = 50)
    print("Execute Time:", datetime.now() - start)
    return max_energy


if __name__ == '__main__':
    param = []
    for i in sys.argv:
        if i != "AnnealingSim.py":
            param.append(i)
    try:
        if "AnnealingSim.py" in param[0]:
            if "python3" in param[1]:
                alpha = param[2]
                beta = param[3]
                count_iter = param[4]
                start_temperature = param[5]
                config_name = param[6]
                h_board = param[7]
                w_board = param[8]
                grid_size = param[9]
            else:
                alpha = param[1]
                beta = param[2]
                count_iter = param[3]
                start_temperature = param[4]
                config_name = param[5]
                h_board = param[6]
                w_board = param[7]
                grid_size = param[8]
        else:
            alpha = param[0]
            beta = param[1]
            count_iter = param[2]
            start_temperature = param[3]
            config_name = param[4]
            h_board = param[5]
            w_board = param[6]
            grid_size = param[7]
        simulation(int(alpha), int(beta), int(count_iter), float(start_temperature), config_name, int(h_board), int(w_board), int(grid_size))
    except IndexError:
        print("Не все данные введены кооректно, попробуйте еще раз!!!")






