import random
import numpy as np
import math
import copy

X = 5
Y = 3
T = 200
SERVICE_POLICY = "FIFO"

in_system_processes = dict()
finished_processes = dict()
time = 0
process_number = 1
next_process_in = -1
is_server_busy = False
server_free_in = -1
current_process_in_server = -1


def generate_random_time(service_type):
    param = X if service_type == "interarrival" else Y
    return math.ceil((-60 / param) * np.log(1 - random.random()))


def generate_process():
    global next_process_in, process_number
    if next_process_in == time:
        interarrival = generate_random_time("interarrival")
        service_time = generate_random_time("service")
        in_system_processes[process_number] = {"arrival_time": time, "service_time": service_time}
        print(f"process number {process_number} was added with arrival time = {time}, service time = {service_time}")
        print(f"next process will be in system {interarrival} seconds later.")
        process_number += 1
        next_process_in = time + interarrival


def server():
    global is_server_busy, server_free_in, current_process_in_server
    if server_free_in == time:
        is_server_busy = False
        in_system_processes[current_process_in_server]["out_server_time"] = time
        current_process = copy.deepcopy(in_system_processes[current_process_in_server])
        finished_processes[current_process_in_server] = current_process
        del in_system_processes[current_process_in_server]
    if len(in_system_processes) != 0 and not is_server_busy:
        if SERVICE_POLICY == "FIFO":
            ids = in_system_processes.keys()
            current_id = min(ids)
            in_system_processes[current_id]["in_server_time"] = time
            current_process = in_system_processes[current_id]
            current_process_in_server = current_id
            service_time = current_process["service_time"]
            is_server_busy = True
            server_free_in = time + service_time
        elif SERVICE_POLICY == "WRR":
            pass
        elif SERVICE_POLICY == "NPPS":
            pass


def start():
    global time, in_system_processes, process_number, next_process_in
    if time == 0:
        interarrival = generate_random_time("interarrival")
        service_time = generate_random_time("service")
        in_system_processes[process_number] = {"arrival_time": time, "service_time": service_time}
        print(f"process number {process_number} was added with arrival time = {time}, service time = {service_time}.")
        print(f"next process will be in system {interarrival} seconds later.")
        process_number += 1
        next_process_in = time + interarrival
    while time <= T:
        generate_process()
        server()
        time += 1


if __name__ == '__main__':
    start()
