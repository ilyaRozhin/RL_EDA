import PCB
import math
import random


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
        hpwl = board.HPWL()
        if hpwl == 0:
            self.reward = -100
        else:
            self.reward = alpha / hpwl + beta * board.location_density()

    def expected_sarsa(self, alpha, gamma, new_state):
        """
        expected_sarsa рассчитывает значения оценок ценностей действий нового состояния.
        :param alpha: весовой коэффициент.
        :param gamma: коэффициент затухания.
        :param new_state: новое состояние системы.
        """
        exp_val = 0
        sum_choice = 0
        for j in new_state.counter_action.values():
            sum_choice += j
        for j in new_state.ratings.keys():
            if sum_choice != 0:
                exp_val += new_state.counter_action[j] * new_state.ratings[j] / sum_choice
        self.ratings[self.chosen_action] += alpha * (new_state.reward + gamma * exp_val - self.ratings[self.chosen_action])


class Agent:
    """
    Agent класс предназначеный для интерпретации агента системы.
    """
    def __init__(self, board, config, epsilon, alpha, beta, gamma, alpha_sarsa, work_mode=True):
        """
        Конструктор создает множество состояний, по имеющейся конфигурации платы.
        :param board: печатная плата.
        :param config: конфигурация печатной платы.
        :param epsilon: мера исследования.
        :param work_mode: один из двух вариантов хранения состояний. False - одна матрица состояний. True - для каждого своя.
        """
        self.environment = board
        self.work_mode = work_mode
        self.config = [s for s in config]
        self.locations = []
        self.epsilon = epsilon
        self.alpha = alpha
        self.beta = beta
        self.gamma = gamma
        self.alpha_sarsa = alpha_sarsa
        self.images = []
        self.max_image = []
        self.max_reward = 0
        self.massRewards = []
        h = board.height
        w = board.width
        grid = board.gridDivisionSize
        horizontal = math.floor(w / grid)
        vertical = math.floor(h / grid)
        if work_mode:
            self.element_states = [[[State(j, s) for s in range(0, vertical)] for j in range(0, horizontal)] for _ in
                                   board.elements]
            self.init_task(alpha, beta)
        else:
            self.element_states = [[State(j, s) for s in range(0, vertical)] for j in range(0, horizontal)]
            self.experimental_init_task(alpha, beta)

    def rebuild_board(self, locations):
        """
        rebuild_board предназначена для пересоздания печатной платы.
        :param locations: измененные координаты элементов.
        """
        h = self.environment.height
        w = self.environment.width
        grid = self.environment.gridDivisionSize
        len_conf = len(locations)
        self.environment = PCB.Board(w, h, grid)
        for s in range(0, len_conf):
            element = self.config[s][0]
            x = locations[s][0]
            y = locations[s][1]
            rotation = self.config[s][3]
            requirements = self.config[s][4]
            self.environment.append_element(element, x, y, rotation, requirements)

    def init_task(self, alpha, beta):
        """
        init_task инициализирует множество состояний системы.
        """
        locations = []
        num_elements = len(self.environment.elements)
        x_max = len(self.element_states[0])-1
        y_max = len(self.element_states[0][0])-1
        for s in range(0, num_elements):
            x = random.randint(0, x_max)
            y = random.randint(0, y_max)
            self.element_states[s][x][y].in_this_state = True
            locations.append([x, y])
        self.rebuild_board(locations)
        self.locations = locations
        self.image_state()
        self.max_image.append(self.images[0])

    def experimental_init_task(self, alpha, beta):
        """
        experimental_init_task экспериментальная инициализация на одной матрице состояний.
        """
        locations = []
        num_elements = len(self.environment.elements)
        x_nums = len(self.element_states)-1
        y_nums = len(self.element_states[0])-1
        for s in range(0, num_elements):
            x = random.randint(0, x_nums)
            y = random.randint(0,  y_nums)
            self.element_states[x][y].in_this_state = True
            locations.append([x, y])
        self.locations = locations
        self.rebuild_board(locations)
        self.image_state()
        self.max_image.append(self.images[0])

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
        if self.work_mode:
            for j in self.element_states[n][x][y].ratings.values():
                if j != 0:
                    return False
        else:
            for j in self.element_states[x][y].ratings.values():
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
        if self.work_mode:
            max_rating = self.element_states[n][x][y].ratings[action]
            for s in self.element_states[n][x][y].ratings.keys():
                if self.element_states[n][x][y].ratings[s] > max_rating:
                    action = s
                    max_rating = self.element_states[n][x][y].ratings[s]
        else:
            max_rating = self.element_states[x][y].ratings[action]
            for s in self.element_states[x][y].ratings.keys():
                if self.element_states[x][y].ratings[s] > max_rating:
                    action = s
                    max_rating = self.element_states[x][y].ratings[s]
        return action

    def chose_action(self, n, x, y):
        """
        chose_action выбирает действие в соотвествии с epsilon-жадной стратегией.
        :param n: номер элемента.
        :param x: абсцисса элемента.
        :param y: ордината элемента.
        :return: возвращает выбранное действие.
        """
        if self.work_mode:
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
        else:
            if self.rating_is_zero(n, x, y):
                action = random.choice(["left", "up", "down", "right"])
            else:
                action = self.max_rating(n, x, y)
                if random.random() <= self.epsilon:
                    actions = ["left", "up", "down", "right"]
                    actions.remove(action)
                    action = random.choice(actions)
            self.element_states[x][y].counter_action[action] += 1
            self.element_states[x][y].chosen_action = action
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
        if self.work_mode:
            y_max = len(self.element_states[n][0])
            x_max = len(self.element_states[n])
        else:
            y_max = len(self.element_states[0])
            x_max = len(self.element_states)
        if action == "up":
            y = old_location[1] - step
            if y < 0:
                self.locations[n][1] = y + step
            else:
                self.locations[n][1] = y
        elif action == "down":
            y = old_location[1] + step
            if y >= y_max:
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
            if x >= x_max:
                self.locations[n][0] = x - step
            else:
                self.locations[n][0] = x
        return self.locations[n][0], self.locations[n][1]

    def full_reward(self, alpha, beta):
        actual_error = self.environment.design_error()
        hpwl = self.environment.HPWL()
        if hpwl == 0:
            reward = -100
        else:
            reward = alpha / hpwl + beta * self.environment.location_density()
        if actual_error == 0:
            reward *= 10
        else:
            reward -= actual_error
        return reward

    def transition(self, alpha, beta, gamma, full_on, create_gif):
        """
        transition отвечает за обновление конфигурации платы, на основании вырабатываемой стратегии.
        """
        num_locations = len(self.locations)
        last_error = self.environment.design_error()
        if full_on:
            reward = self.full_reward(alpha, beta)
            if self.environment.design_error() == 0 and self.max_reward < reward:
                self.max_image.clear()
                self.max_image.append(self.environment.show_board())
                self.max_reward = reward
            self.massRewards.append(reward)
        else:
            reward = 0
        for n in range(0, num_locations):
            x = self.locations[n][0]
            y = self.locations[n][1]
            action = self.chose_action(n, x, y)
            old_location = [x, y]
            self.element_states[n][x][y].in_this_state = False
            self.locations[n][0], self.locations[n][1] = self.action_moving(action, old_location, 1, n)
            x = self.locations[n][0]
            y = self.locations[n][1]
            self.element_states[n][x][y].in_this_state = True
            self.rebuild_board(self.locations)
            new_state = self.element_states[n][x][y]
            if not full_on:
                actual_error = self.environment.design_error()
                design_errors = last_error - actual_error
                self.element_states[n][x][y].calculate_reward(alpha, beta, self.environment)
                if actual_error == 0:
                    self.element_states[n][x][y].reward *= 10
                else:
                    self.element_states[n][x][y].reward -= design_errors * 10
                self.element_states[n][old_location[0]][old_location[1]].expected_sarsa(self.alpha_sarsa, gamma, new_state)
                last_error = actual_error
                reward += self.element_states[n][x][y].reward
                if actual_error == 0 and self.max_reward < self.element_states[n][x][y].reward:
                    self.max_image.clear()
                    self.max_image.append(self.environment.show_board())
                    self.max_reward = self.element_states[n][x][y].reward
            else:
                self.element_states[n][x][y].reward = reward
                new_state = self.element_states[n][x][y]
                self.element_states[n][old_location[0]][old_location[1]].expected_sarsa(self.alpha_sarsa, gamma, new_state)
            if create_gif:
                self.image_state()

    def experimental_transition(self, alpha, beta, gamma, full_on, create_gif):
        """
        experimental_transition экспериментальный регулятор переходов.
        """
        num_locations = len(self.locations)
        last_error = self.environment.design_error()
        if full_on:
            reward = self.full_reward(alpha, beta)
            if self.environment.design_error() == 0 and self.max_reward < reward:
                self.max_image.clear()
                self.max_image.append(self.environment.show_board())
                self.max_reward = reward
            self.massRewards.append(reward)
        else:
            reward = 0
        for n in range(0, num_locations):
            x = self.locations[n][0]
            y = self.locations[n][1]
            action = self.chose_action(n, x, y)
            old_location = [x, y]
            self.element_states[x][y].in_this_state = False
            self.locations[n][0], self.locations[n][1] = self.action_moving(action, old_location, 1, n)
            x = self.locations[n][0]
            y = self.locations[n][1]
            self.element_states[x][y].in_this_state = True
            self.rebuild_board(self.locations)
            new_state = self.element_states[x][y]
            if not full_on:
                actual_error = self.environment.design_error()
                design_errors = last_error - actual_error
                self.element_states[x][y].calculate_reward(alpha, beta, self.environment)
                if actual_error == 0:
                    self.element_states[x][y].reward *= 10
                else:
                    self.element_states[x][y].reward -= design_errors * 10
                self.element_states[old_location[0]][old_location[1]].expected_sarsa(self.alpha_sarsa, gamma, new_state)
                last_error = actual_error
                reward += self.element_states[x][y].reward
                if actual_error == 0 and self.max_reward < self.element_states[x][y].reward:
                    self.max_image.clear()
                    self.max_image.append(self.environment.show_board())
                    self.max_reward = self.element_states[x][y].reward
            else:
                self.element_states[x][y].reward = reward
                new_state = self.element_states[x][y]
                self.element_states[old_location[0]][old_location[1]].expected_sarsa(self.alpha_sarsa, gamma, new_state)
            if create_gif:
                self.image_state()

    def launch(self, count_iter, count_episodes, create_gif, full_on):
        """
        launch отвечает за запуск процесса обучения.
        :param count_iter: количество временных отрезков для обучения.
        :param create_gif: создавать ли гифку или нет.
        """
        max_mass_images = []
        max_mass_rewards = []
        for n in range(0, count_episodes):
            if self.work_mode:
                for s in range(0, count_iter):
                    print("*******************", s, "*******************")
                    self.transition(self.alpha, self.beta, self.gamma, full_on, create_gif)
            else:
                for s in range(0, count_iter):
                    print("*******************", s, "*******************")
                    self.experimental_transition(self.alpha, self.beta,  self.gamma, full_on, create_gif)
            if create_gif:
                self.images[0].save('dynamic.gif', save_all=True, append_images=self.images[1:], optimize=True,
                                    duration=0.000000001, loop=0)
            if self.max_reward > 0:
                max_mass_images.append(self.max_image[0])
                max_mass_rewards.append(self.max_reward)
            self.max_image.clear()
            self.images.clear()
            self.max_reward = 0
            if self.work_mode:
                self.init_task(self.alpha, self.beta)
            else:
                self.experimental_init_task(self.alpha, self.beta)
        return max_mass_images, max_mass_rewards
