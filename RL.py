import main
import math
import random
import configurations


class State:

    def __init__(self, x, y, in_this_state=False):
        self.location = (x, y)
        self.rating = {"up": 0, "down": 0, "left": 0, "right": 0}
        self.reward = 0
        self.counter_action = {"up": 0, "down": 0, "left": 0, "right": 0}
        self.in_this_state = in_this_state
        self.last_chosen_action = ""

    def reward_calculation(self, alpha, beta, board):
        if board.design_error():
            self.reward -= 100
        else:
            self.reward = alpha*board.HPWL() + beta*board.location_density()

    def expected_sarsa(self, alpha, gamma, new_state):
        next_mat = 0
        sum_choice = 0
        for i in new_state.rating.values():
            sum_choice += i
        for i in new_state.rating.keys():
            next_mat += new_state.counter_action[i]*new_state.rating[i]/sum_choice
        self.rating[self.last_chosen_action] += alpha*(self.reward + gamma*next_mat
                                                       - self.rating[self.last_chosen_action])


class Agent:

    def __init__(self, board, config, epsilon):
        self.environment = board
        self.element_states = [[[State(j, s) for s in range(1, math.floor(board.height/board.gridDivisionSize))]
                                for j in range(1, math.floor(board.width/board.gridDivisionSize))]
                               for i in board.elements]
        self.config = [i for i in config]
        self.locations = []
        self.epsilon = epsilon
        self.image_for_GIF = []
        self.init_task()

    def rebuild_board(self, locations):
        self.environment = main.MainBoard(self.environment.width, self.environment.height,
                                          self.environment.gridDivisionSize)
        for i in range(0, len(self.config)):
            self.environment.append_element(self.config[i][0], locations[i][0], locations[i][1], self.config[i][3],
                                            self.config[i][4])

    def init_task(self):
        mass_location_states = []
        for i in range(0, len(self.environment.elements)):
            num = random.randint(0, len(self.element_states[i])*len(self.element_states[i][0]))
            self.element_states[i][math.floor(num/len(self.element_states[i]))][num
                - math.floor(num/len(self.element_states[i]))].in_this_state = True
            mass_location_states.append((math.floor(num/len(self.element_states[i])), num
                - math.floor(num/len(self.element_states[i]))))
        self.locations = [i for i in mass_location_states]
        self.rebuild_board(self.locations)
        self.image_for_GIF.append(self.image_state())
        mass_location_states.clear()

    def image_state(self):
        return self.environment.show_board()

    def transition(self):
        rating_is_zero = True
        mass = ["left", "up", "down", "right"]
        for i in range(0, len(self.locations)):
            for j in self.element_states[i][self.locations[i][0]][self.locations[i][1]].rating:
                if j != 0:
                    rating_is_zero = False
                    break
            if rating_is_zero:
                chosen_action = random.choice(mass)
                self.element_states[i][self.locations[i][0]][self.locations[i][1]].counter_action[chosen_action] += 1
                self.element_states[i][self.locations[i][0]][self.locations[i][1]].last_chosen_action = chosen_action
            else:
                chosen_action = "up"
                max_rating = self.element_states[i][self.locations[i][0]][self.locations[i][1]].rating["up"]
                for s in self.element_states[i][self.locations[i][0]][self.locations[i][1]].rating.keys():
                    if self.element_states[i][self.locations[i][0]][self.locations[i][1]].rating[s] > max_rating:
                        chosen_action = s
                        max_rating = self.element_states[i][self.locations[i][0]][self.locations[i][1]].rating[s]
                if random.random() > self.epsilon:
                    self.element_states[i][self.locations[i][0]][self.locations[i][1]].counter_action[
                        chosen_action] += 1
                    self.element_states[i][self.locations[i][0]][
                        self.locations[i][1]].last_chosen_action = chosen_action
                else:
                    buf = chosen_action
                    mass.remove(chosen_action)
                    chosen_action = random.choice(mass)
                    mass.append(buf)
                    self.element_states[i][self.locations[i][0]][self.locations[i][1]].counter_action[
                        chosen_action] += 1
                    self.element_states[i][self.locations[i][0]][
                        self.locations[i][1]].last_chosen_action = chosen_action
            old_location = self.locations[i]
            self.element_states[i][self.locations[i][0]][self.locations[i][1]].in_this_state = False
            if chosen_action == "up":
                y = old_location[1] - 1
                if y < 0:
                    self.locations[i][1] = y + 1
                else:
                    self.locations[i][1] = y
            elif chosen_action == "down":
                y = old_location[1] + 1
                if y >= len(self.element_states[i][0]):
                    self.locations[i][1] = y - 1
                else:
                    self.locations[i][1] = y
            elif chosen_action == "left":
                x = old_location[0] - 1
                if x < 0:
                    self.locations[i][0] = x + 1
                else:
                    self.locations[i][0] = x
            elif chosen_action == "right":
                x = old_location[0] + 1
                if x >= len(self.element_states[i]):
                    self.locations[i][0] = x - 1
                else:
                    self.locations[i][0] = x
            self.rebuild_board(self.locations)
            self.element_states[i][old_location[0]][old_location[1]].reward_calculation(1, 1, self.environment)
            new_state = self.element_states[i][self.locations[i][0]][self.locations[i][1]]
            self.element_states[i][old_location[0]][old_location[1]].\
                expected_sarsa(0.9, 0.9, new_state)
            self.image_for_GIF.append(self.image_state())

    def launch(self, count_iter):
        for i in range(0, count_iter):
            self.transition()
        self.image_for_GIF[0].save(
            'pcb_result.gif',
            save_all=True,
            append_images=self.image_for_GIF[1:],
            optimize=False,
            duration=40,
            loop=0
        )


if __name__ == '__main__':
    config_dict = configurations.init_configuration_dict()
    new_board = main.MainBoard(600, 600, 8)
    a = Agent(new_board, config_dict["config1"], 0.9)
