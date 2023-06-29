import random
import numpy as np
import math

X = 5
Y = 3
T = 1000

processes_list = dict()
time = 0
process_number = 1
next_process_in = -1


def generate_random_time(service_type):
    param = X if service_type == "interarrival" else Y
    return math.floor((-60 / param) * np.log(1 - random.random()))


def start():
    global time, processes_list, process_number, next_process_in
    if time == 0:
        interarrival = generate_random_time("interarrival")
        service_time = generate_random_time("service")
        processes_list[process_number] = {"arrival_time": time, "service_time": service_time}
        process_number += 1
        next_process_in = time + interarrival


if __name__ == '__main__':
    start()
