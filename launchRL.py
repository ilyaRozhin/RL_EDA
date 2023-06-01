import Config
import matplotlib.pyplot as plt
import sys
from PCB import Board
from RL import Agent
from datetime import datetime
from PIL import ImageShow


def main_function(name_config, h_board, w_board, grid_size, alpha, beta, gamma, alpha_sarsa, work_mode, full_on, count_of_iter, count_of_episodes, epsilon):
    config_dict = Config.init_configuration_dict()
    new_board = Board(h_board, w_board, grid_size)
    config_name = name_config
    for i in config_dict[config_name]:
        new_board.append_element(i[0], i[1], i[2], i[3], i[4])
    a = Agent(new_board, config_dict[config_name], epsilon, alpha, beta, gamma, alpha_sarsa, work_mode)
    start = datetime.now()
    a.images[0].save("results/StartImage_" + config_name + "&work=" + str(work_mode) + ".png")
    max_images, max_rewards = a.launch(count_of_iter, count_of_episodes, False, full_on)
    print(datetime.now() - start)
    if len(max_rewards):
        index_max_reward = max_rewards.index(max(max_rewards))
        if len(max_images):
            max_images[index_max_reward].save("results/MaxImage_" + config_name + "&work=" + str(work_mode) + ".png")
        plt.plot([i for i in range(0, len(max_rewards))], max_rewards)
        plt.title("Value of Rewards")
        plt.xlabel("Episodes")
        plt.ylabel("Max value of Total Reward")
        plt.savefig("results/" + config_name + "_values_of_rewards.png", dpi = 50)


if __name__ == '__main__':
    param = []
    for i in sys.argv:
        if i != "launchRL.py":
            param.append(i)
    try:
        if "launchRL.py" in param[0]:
            if "python3" in param[1]:
                name_config = param[2]
                h_board = param[3]
                w_board = param[4]
                grid_size = param[5]
                alpha = param[6]
                beta = param[7]
                gamma = param[8]
                alpha_sarsa = param[9]
                work_mode = param[10]
                full_on = param[11]
                count_of_iter = param[12]
                count_of_episodes = param[13]
                epsilon = param[14]
            else:
                name_config = param[1]
                h_board = param[2]
                w_board = param[3]
                grid_size = param[4]
                alpha = param[5]
                beta = param[6]
                gamma = param[7]
                alpha_sarsa = param[8]
                work_mode = param[9]
                full_on = param[10]
                count_of_iter = param[11]
                count_of_episodes = param[12]
                epsilon = param[13]
        else:
            name_config = param[0]
            h_board = param[1]
            w_board = param[2]
            grid_size = param[3]
            alpha = param[4]
            beta = param[5]
            gamma = param[6]
            alpha_sarsa = param[7]
            work_mode = param[8]
            full_on = param[9]
            count_of_iter = param[10]
            count_of_episodes = param[11]
            epsilon = param[12]
        main_function(name_config, int(h_board), int(w_board), int(grid_size), float(alpha), float(beta), float(gamma), float(alpha_sarsa), bool(work_mode), bool(full_on), int(count_of_iter), int(count_of_episodes), float(epsilon))
    except IndexError:
        print("Не все данные введены кооректно, попробуйте еще раз!!!")
