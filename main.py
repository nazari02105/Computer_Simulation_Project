import random
import numpy as np
import math
import copy

X = 5
Y = 3
T = 200
SERVICE_POLICY = "WRR"

in_system_processes = dict()
finished_processes = dict()
time = 0
process_number = 1
next_process_in = -1
is_server_busy = False
server_free_in = -1
current_process_in_server = -1

# from low to high
WRR_Lines = [[]for _ in range(3)]
WRR_Weights = [3,2,1] 
Last_WRR_state = [3,3] #(priority, left)

def generate_random_time(service_type):
    param = X if service_type == "interarrival" else Y
    return math.ceil((-60 / param) * np.log(1 - random.random()))


def generate_priority():
    random_number = random.random()
    if 0 <= random_number <= 0.2:
        return 3
    elif 0.2 < random_number <= 0.5:
        return 2
    else:
        return 1


def generate_process():
    if next_process_in == time:
        store_process()

def store_process():
    global next_process_in, process_number
    interarrival = generate_random_time("interarrival")
    service_time = generate_random_time("service")
    priority = generate_priority()
    in_system_processes[process_number] = {"arrival_time": time, "service_time": service_time, "priority": priority}
        # add a process to its line
    WRR_Lines[priority-1].append(process_number)

    print(f"process number {process_number} was added with arrival time = {time}, "
              f"service time = {service_time} and priority = {priority}.")
    print(f"next process will be in system {interarrival} seconds later.")
    process_number += 1
    next_process_in = time + interarrival


def get_next_process_for_npps():
    temp = copy.deepcopy(in_system_processes)
    max_priority = -1
    for key in temp.keys():
        if temp[key]["priority"] > max_priority:
            max_priority = temp[key]["priority"]
    least_time = math.inf
    for key in temp.keys():
        if temp[key]["priority"] == max_priority and temp[key]["arrival_time"] < least_time:
            least_time = temp[key]["arrival_time"]
    to_return = None
    for key in temp.keys():
        if temp[key]["priority"] == max_priority and temp[key]["arrival_time"] == least_time:
            to_return = key
    return to_return


def server():
    global is_server_busy, server_free_in, current_process_in_server
    if server_free_in == time:
        is_server_busy = False
        in_system_processes[current_process_in_server]["out_server_time"] = time
        current_process = copy.deepcopy(in_system_processes[current_process_in_server])
        finished_processes[current_process_in_server] = current_process
        print(f"process number {current_process_in_server} released server in {time}")
        del in_system_processes[current_process_in_server]
    if len(in_system_processes) != 0 and not is_server_busy:
        if SERVICE_POLICY == "FIFO":
            ids = in_system_processes.keys()
            current_id = min(ids)
            select_process(current_id)

        elif SERVICE_POLICY == "WRR":
            get_next_process_WRR()
        elif SERVICE_POLICY == "NPPS":
            current_id = get_next_process_for_npps()
            select_process(current_id)

def get_next_process_WRR():
    global Last_WRR_state
    if Last_WRR_state[0] == 3 and Last_WRR_state[1] > 0:
        if len(WRR_Lines[2]):
            Last_WRR_state = [3,Last_WRR_state[1]-1]
            current_id = WRR_Lines[2].pop(0)
            select_process(current_id)
            print(f"A process executed ftom line: 3")
        elif len(WRR_Lines[1]):
            Last_WRR_state = [2,1]
            current_id = WRR_Lines[1].pop(0)
            select_process(current_id) 
            print(f"A process executed ftom line: 2")
        elif len(WRR_Lines[0]):
            Last_WRR_state = [1,0]
            current_id = WRR_Lines[0].pop(0)
            select_process(current_id) 
            print(f"A process executed ftom line: 1")
        else:
            pass
    elif Last_WRR_state[0] == 2 and Last_WRR_state[1] > 0:
        if len(WRR_Lines[1]):
            Last_WRR_state = [2,Last_WRR_state[1]-1]
            current_id = WRR_Lines[1].pop(0)
            select_process(current_id)
            print(f"A process executed ftom line: 2")
        elif len(WRR_Lines[0]):
            Last_WRR_state = [1,0]
            current_id = WRR_Lines[0].pop(0)
            select_process(current_id) 
            print(f"A process executed ftom line: 1")
        elif len(WRR_Lines[2]):
            Last_WRR_state = [3,2]
            current_id = WRR_Lines[2].pop(0)
            select_process(current_id) 
            print(f"A process executed ftom line: 3")
        else:
            pass
    elif Last_WRR_state[0] == 1 and Last_WRR_state[1] > 0:
        if len(WRR_Lines[0]):
            Last_WRR_state = [1,Last_WRR_state[1]-1]
            current_id = WRR_Lines[0].pop(0)
            select_process(current_id)
            print(f"A process executed ftom line: 1")
        elif len(WRR_Lines[2]):
            Last_WRR_state = [3,2]
            current_id = WRR_Lines[2].pop(0)
            select_process(current_id) 
            print(f"A process executed ftom line: 3")
        elif len(WRR_Lines[1]):
            Last_WRR_state = [2,1]
            current_id = WRR_Lines[1].pop(0)
            select_process(current_id) 
            print(f"A process executed ftom line: 2")
        else:
            pass


def select_process(current_id):
    global is_server_busy, server_free_in, current_process_in_server
    in_system_processes[current_id]["in_server_time"] = time
    current_process = in_system_processes[current_id]
    current_process_in_server = current_id
    service_time = current_process["service_time"]
    is_server_busy = True
    server_free_in = time + service_time
    print(f"process number {current_id} got server in {time} and will hold it for {service_time} seconds")


def start():
    global time, in_system_processes, process_number, next_process_in
    if time == 0:
       store_process()
    while time <= T:
        generate_process()
        server()
        time += 1


if __name__ == '__main__':
    start()
