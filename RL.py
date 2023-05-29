import PCB
import math
import random
import Config
from PIL import ImageShow
import matplotlib.pyplot as plt
from datetime import datetime


class State:
    """
    State интерпретация состояния МППР.
    """
    def __init__(self, x, y, in_this_state=False):
        """
        Коснтруктор определяет координаты состояния и находится ли элемент в нем.
        :param x: Абсцисса элемента.
        :param y: Ордината элемента.
        :param in_this_state: Факт нахождения в данном состояние.
        """
        self.location = (x, y)
        self.ratings = {"up": 0, "down": 0, "left": 0, "right": 0}
        self.reward = 0
        self.counter_action = {"up": 0, "down": 0, "left": 0, "right": 0}
        self.in_this_state = in_this_state
        self.chosen_action = ""

    def calculate_reward(self, alpha, beta, board):
        """
        calculate_reward рассчитывает вознаграждения на основании значения оценочных критериев.
        :param alpha: первый весовой коэффициент.
        :param beta: второй весовой коэффициент.
        :param board: объект класса Board.
        """
        if board.HPWL() == 0:
            self.reward = beta * board.location_density() - 100 * board.design_error()
        else:
            self.reward = beta * board.location_density() + alpha / board.HPWL() - 100 * board.design_error()
        print("Density: ", board.location_density(), "HPWL:", board.HPWL(), "Errors:", board.design_error())

    def expected_sarsa(self, alpha, gamma, new_state):
        """
        expected_sarsa рассчитывает значения оценок ценностей действий нового состояния.
        :param alpha: весовой коэффициент.
        :param gamma: коэффициент затухания.
        :param new_state: новое состояние системы.
        """
        exp_val = 0
        sum_choice = 0
        rate = self.ratings[self.chosen_action]
        for j in new_state.counter_action.values():
            sum_choice += j
        for j in new_state.ratings.keys():
            if sum_choice != 0:
                exp_val += new_state.counter_action[j] * new_state.ratings[j] / sum_choice
        rate += alpha * (new_state.reward + gamma * exp_val - rate)


class Agent:
    """
    Agent класс предназначеный для интерпретации агента системы.
    """
    def __init__(self, board, config, epsilon):
        """
        Конструктор создает множество состояний, по имеющейся конфигурации платы.
        :param board: печатная плата.
        :param config: конфигурация печатной платы.
        :param epsilon: мера исследования.
        """
        h = board.height
        w = board.width
        grid = board.gridDivisionSize
        horizontal = math.floor(w/grid)
        vertical = math.floor(h/grid)
        self.environment = board
        self.config = [s for s in config]
        self.element_states = [[[State(j, s) for s in range(0, vertical)] for j in range(0, horizontal)] for _ in board.elements]
        self.locations = []
        self.epsilon = epsilon
        self.images = []
        self.massRewards = []
        self.init_task()

    def rebuild_board(self, locations):
        """
        rebuild_board предназначена для пересоздания печатной платы.
        :param locations: измененные координаты элементов.
        """
        h = self.environment.height
        w = self.environment.width
        grid = self.environment.gridDivisionSize
        len_conf = len(self.config)
        self.environment = PCB.Board(w, h, grid)
        for s in range(0, len_conf):
            element = self.config[s][0]
            x = locations[s][0]
            y = locations[s][1]
            rotation = self.config[s][3]
            requirements = self.config[s][4]
            self.environment.append_element(element, x, y, rotation, requirements)

    def init_task(self):
        """
        init_task инициализирует множество состояний системы.
        """
        locations = []
        num_elements = len(self.environment.elements)
        reward = 0
        for s in range(0, num_elements):
            x = random.randint(0, len(self.element_states[s])-1)
            y = random.randint(0, len(self.element_states[s][0])-1)
            self.element_states[s][x][y].in_this_state = True
            locations.append([x, y])
        self.locations = locations
        self.rebuild_board(locations)
        self.image_state()
        num_locations = len(self.locations)
        for s in range(0, num_locations):
            x = self.locations[s][0]
            y = self.locations[s][1]
            self.element_states[s][x][y].calculate_reward(0.9, 0.7, self.environment)
            reward += self.element_states[s][x][y].reward
        self.massRewards.append(reward)

    def image_state(self):
        """
        image_state добавляет картинку платы в актуальной конфигурации.
        """
        self.images.append(self.environment.show_board())

    def rating_is_zero(self, n, x, y):
        """
        rating_is_zero проверяет все ли оценки ценностей действий равны нулю.
        :param n: номер элемента.
        :param x: абсцисса элемента.
        :param y: ордината элемента.
        :return: True, если все оценки равны нулю, False в обратном случае.
        """
        for j in self.element_states[n][x][y].ratings.values():  # Было [y][x]
            if j != 0:
                return False
        return True

    def max_rating(self, n, x, y):
        """
        max_rating функция поиска максимальной оценки среди имеющихся.
        :param n: номер элемента.
        :param x: абсцисса элемента.
        :param y: ордината элемента.
        :return: True, если все оценки равны нулю, False в обратном случае.
        """
        action = "up"
        max_rating = self.element_states[n][x][y].ratings["up"]
        for s in self.element_states[n][x][y].ratings.keys():
            if self.element_states[n][x][y].ratings[s] > max_rating:
                action = s
                max_rating = self.element_states[n][x][y].ratings[s]
        return action

    def chose_action(self, n, x, y):
        """
        chose_action выбирает действие в соотвествии с epsilon-жадной стратегией.
        :param n: номер элемента.
        :param x: абсцисса элемента.
        :param y: ордината элемента.
        :return: возвращает выбранное действие.
        """
        if self.rating_is_zero(n, x, y):
            action = random.choice(["left", "up", "down", "right"])
        else:
            action = self.max_rating(n, x, y)
            if random.random() <= self.epsilon:
                actions = ["left", "up", "down", "right"]
                actions.remove(action)
                action = random.choice(actions)
        self.element_states[n][x][y].counter_action[action] += 1
        self.element_states[n][x][y].chosen_action = action
        return action

    def action_moving(self, action, old_location, step, n):
        """
        action_moving функция перемещающая элемент из старого состояния в актуальное.
        :param action: выбранное действие.
        :param old_location: старое состояние.
        :param step: размер шага перемещения.
        :param n: номер рассматриваемого элемента.
        :return: новые координаты.
        """
        if action == "up":
            y = old_location[1] - step
            if y < 0:
                self.locations[n][1] = y + step
            else:
                self.locations[n][1] = y
        elif action == "down":
            y = old_location[1] + step
            if y >= len(self.element_states[n][0]):
                self.locations[n][1] = y - step
            else:
                self.locations[n][1] = y
        elif action == "left":
            x = old_location[0] - step
            if x < 0:
                self.locations[n][0] = x + step
            else:
                self.locations[n][0] = x
        elif action == "right":
            x = old_location[0] + step
            if x >= len(self.element_states[n]):
                self.locations[n][0] = x - step
            else:
                self.locations[n][0] = x
        return self.locations[n][0], self.locations[n][1]

    def transition(self, alpha, beta, gamma):
        """
        transition отвечает за обновление конфигурации платы, на основании вырабатываемой стратегии.
        """
        num_locations = len(self.locations)
        for n in range(0, num_locations):
            x = self.locations[n][0]
            y = self.locations[n][1]
            action = self.chose_action(n, x, y)
            old_location = [x, y]
            self.element_states[n][x][y].in_this_state = False
            x, y = self.action_moving(action, old_location, 1, n)
            self.element_states[n][x][y].in_this_state = True
            self.rebuild_board(self.locations)
            self.element_states[n][x][y].calculate_reward(alpha, beta, self.environment)

            print(self.element_states[n][x][y].reward)

            new_state = self.element_states[n][x][y]
            self.element_states[n][old_location[0]][old_location[1]].expected_sarsa(0.9, gamma, new_state)
            self.image_state()
        reward = 0
        for n in range(0, len(self.locations)):
            x = self.locations[n][0]
            y = self.locations[n][1]
            self.element_states[n][x][y].calculate_reward(1, 1, self.environment)
            reward += self.element_states[n][x][y].reward
        self.massRewards.append(reward)

    def launch(self, count_iter, create_gif):
        """
        launch отвечает за запуск процесса обучения.
        :param count_iter: количество временных отрезков для обучения.
        :param create_gif: создавать ли гифку или нет.
        """
        for s in range(0, count_iter):
            print("*******************", s, "*******************")
            self.transition(0.9, 0.7, 0.1)
        ImageShow.show(self.images[0])
        ImageShow.show(self.images[len(self.images)-1])
        print("FirstReward:", self.massRewards[0], "EndReward:", self.massRewards[len(self.massRewards)-1])
        if create_gif:
            self.images[0].save('pcb_work.gif', save_all=True, append_images=self.images[1:], optimize=True,
                                duration=0.000000001, loop=0)


if __name__ == '__main__':
    config_dict = Config.init_configuration_dict()
    new_board = PCB.Board(40, 40, 8)
    for i in config_dict["config3"]:
        new_board.append_element(i[0], i[1], i[2], i[3], i[4])
    a = Agent(new_board, config_dict["config3"], 0.3)
    ImageShow.show(a.images[0])
    a.environment.design_error()
    #count_of_iter = 800
    #start = datetime.now()
    #a.launch(count_of_iter, True)
    #print(datetime.now() - start)
    #plt.plot([i for i in range(0, count_of_iter+1)], a.massRewards)
    #plt.title("Value of Rewards")
    #plt.xlabel("Count of runs")
    #plt.ylabel("Value of Total Reward")
    #plt.show()

