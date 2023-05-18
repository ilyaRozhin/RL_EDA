import main
import math
import random
import configurations
from PIL import ImageShow
import matplotlib.pyplot as plt


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
            self.reward -= 10
        else:
            self.reward = alpha*board.HPWL() + beta*board.location_density()

    def expected_sarsa(self, alpha, gamma, new_state):
        next_mat = 0
        sum_choice = 0
        for j in new_state.rating.values():
            sum_choice += j
        for j in new_state.rating.keys():
            if sum_choice != 0:
                next_mat += new_state.counter_action[j]*new_state.rating[j]/sum_choice

        print(self.last_chosen_action + "!")
        self.rating[self.last_chosen_action] += alpha*(self.reward + gamma*next_mat - self.rating[self.last_chosen_action])


class Agent:

    def __init__(self, board, config, epsilon):
        self.environment = board
        self.config = [s for s in config]
        self.element_states = [[[State(j, s) for s in range(0, math.floor(board.height/board.gridDivisionSize))]
                                        for j in range(0, math.floor(board.width/board.gridDivisionSize))]
                                for z in board.elements]
        self.locations = []
        self.epsilon = epsilon
        self.image_for_GIF = []
        self.lastImage = []
        self.firstImage = []
        self.firstReward = 0
        self.lastReward = 0
        self.massRewards = []
        self.init_task()

    def rebuild_board(self, locations):
        self.environment = main.MainBoard(self.environment.width, self.environment.height,
                                          self.environment.gridDivisionSize)
        for i in range(0, len(self.config)):
            self.environment.append_element(self.config[i][0], locations[i][0], locations[i][1], self.config[i][3],
                                            self.config[i][4])

    def init_task(self):
        mass_location_states = []
        for index in range(0, len(self.environment.elements)):
            x_new = random.randint(0, len(self.element_states[index])-1)
            y_new = random.randint(0, len(self.element_states[index][0])-1)
            print("New_values:", x_new, y_new)
            self.element_states[index][x_new][y_new].in_this_state = True
            mass_location_states.append([x_new, y_new])

        self.locations = [i for i in mass_location_states]
        self.rebuild_board(self.locations)
        self.image_for_GIF.append(self.image_state())              # Для генерации гифки раскомментить
        #self.lastImage.clear()
        self.firstImage.append(self.image_state())
        #for i in range(0, len(self.locations)):
        #    self.element_states[i][self.locations[i][0]][self.locations[i][1]].reward_calculation(1.5, 0.7,
        #                                                                                          self.environment)
        #    self.firstReward += self.element_states[i][self.locations[i][0]][self.locations[i][1]].reward
        #self.massRewards.append(self.firstReward)
        mass_location_states.clear()

    def image_state(self):
        return self.environment.show_board()

    def transition(self):
        for i in range(0, len(self.locations)):
            rating_is_zero = True
            for j in self.element_states[i][self.locations[i][1]][self.locations[i][0]].rating.values():
                if j != 0:
                    rating_is_zero = False
                    print("Break for rating_is_zero")
                    break
            print(rating_is_zero)
            if rating_is_zero:
                print("***** 0 ******")
                chosen_action = random.choice(["left", "up", "down", "right"])
                print(chosen_action)
                self.element_states[i][self.locations[i][0]][self.locations[i][1]].counter_action[chosen_action] += 1
                self.element_states[i][self.locations[i][0]][self.locations[i][1]].last_chosen_action = chosen_action
            else:
                print("***** 2 ******")
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
                    mass = ["left", "up", "down", "right"]
                    mass.remove(chosen_action)
                    chosen_action = random.choice(mass)
                    self.element_states[i][self.locations[i][0]][self.locations[i][1]].counter_action[
                        chosen_action] += 1
                    self.element_states[i][self.locations[i][0]][
                        self.locations[i][1]].last_chosen_action = chosen_action
            print("***** 1 ******")
            print(self.locations[i][0], self.locations[i][1])
            old_location = []
            old_location.append(self.locations[i][0])
            old_location.append(self.locations[i][1])
            print("Old first:", old_location[0], old_location[1])
            self.element_states[i][self.locations[i][0]][self.locations[i][1]].in_this_state = False
            step_random = 1
            if chosen_action == "up":
                y = old_location[1] - step_random
                if y < 0:
                    self.locations[i][1] = y + step_random
                else:
                    self.locations[i][1] = y
            elif chosen_action == "down":
                y = old_location[1] + step_random
                if y >= len(self.element_states[i][0]):
                    self.locations[i][1] = y - step_random
                else:
                    self.locations[i][1] = y
            elif chosen_action == "left":
                x = old_location[0] - step_random
                if x < 0:
                    self.locations[i][0] = x + step_random
                else:
                    self.locations[i][0] = x
            elif chosen_action == "right":
                x = old_location[0] + step_random
                if x >= len(self.element_states[i]):
                    self.locations[i][0] = x - step_random
                else:
                    self.locations[i][0] = x
            print(self.locations[i][0], self.locations[i][1], old_location[0], old_location[1], len(self.element_states[i][0]))
            self.element_states[i][self.locations[i][0]][self.locations[i][1]].in_this_state = True
            self.rebuild_board(self.locations)
            self.element_states[i][old_location[0]][old_location[1]].reward_calculation(1, 1, self.environment)
            print("Old second:", old_location[0], old_location[1])
            new_state = self.element_states[i][self.locations[i][0]][self.locations[i][1]]
            self.element_states[i][old_location[0]][old_location[1]].\
                expected_sarsa(0.2, 0.9, new_state)
            self.image_for_GIF.append(self.image_state())          ## Для активации гифки раскомментить
            self.lastImage.clear()
            self.lastImage.append(self.image_state())
            self.lastReward = 0
        for i in range(0, len(self.locations)):
            self.element_states[i][self.locations[i][0]][self.locations[i][1]].reward_calculation(3.5, 1,
                                                                                                      self.environment)
            self.lastReward += self.element_states[i][self.locations[i][0]][self.locations[i][1]].reward
        self.massRewards.append(self.lastReward)

    def launch(self, count_iter):
        for i in range(0, count_iter):
            self.transition()
        ImageShow.show(self.firstImage[0])
        ImageShow.show(self.lastImage[0])
        print(self.lastReward, self.firstReward)
        self.image_for_GIF[0].save(
           'pcb_result.gif',
            save_all=True,
            append_images=self.image_for_GIF[1:],
            optimize=True,
            duration=1,
            loop=0
        )


if __name__ == '__main__':
    config_dict = configurations.init_configuration_dict()
    new_board = main.MainBoard(600, 600, 8)
    for i in config_dict["config2"]:
        new_board.append_element(i[0], i[1], i[2], i[3], i[4])
    new_board.show_board_special()
    a = Agent(new_board, config_dict["config2"], 0.2)
    count_of_iter = 800
    a.launch(count_of_iter)
    #x = np.arange(count_of_iter)
    #info = {'reward_first': a.massRewards}
    #y = pd.DataFrame(info)
    #print (y)
    plt.plot([i for i in range(0, count_of_iter)], a.massRewards)
    plt.title("Value of Rewards")
    plt.xlabel("Count of runs")
    plt.ylabel("Value of Total Reward")
    plt.show()

