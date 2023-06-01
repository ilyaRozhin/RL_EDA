from AnnealingSim import simulation
from LaunchRL import main_function
import matplotlib.pyplot as plt
from datetime import datetime


if __name__ == '__main__':
    delta_time_mass = []
    rewards_energy_mass = []
    counter_checks = 100
    for i in range(0, counter_checks):
        start = datetime.now()
        rl_max_reward = main_function("config3", 100, 100, 10, 0.1, 1, 0.3, 1, True, True, 1000, 10, 0.2, True)
        rl_time = datetime.now() - start
        start = datetime.now()
        as_max_energy = simulation(1, 1, 10000, 20, "config3", 100, 100, 10, True)
        as_time = datetime.now() - start
        delta = as_time.total_seconds() - rl_time.total_seconds()
        delta_time_mass.append(delta)
        rewards_energy_mass.append(rl_max_reward/as_max_energy)
    time_plot, = plt.plot([i for i in range(1, counter_checks+1)], delta_time_mass)
    plt.title("Program Execution Time")
    plt.xlabel("Count of Checks")
    plt.ylabel("Delta Time")
    plt.savefig("benchmark_results/times_num=" + str(counter_checks) +".png", dpi=50)
    time_plot.remove()

    plt.plot([i for i in range(1, counter_checks + 1)], rewards_energy_mass)
    plt.title("Rewards and Energy")
    plt.xlabel("Count of Checks")
    plt.ylabel("Ratio Reward to Energy")
    plt.savefig("benchmark_results/reward_num=" + str(counter_checks) + ".png", dpi=50)