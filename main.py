import random
import numpy as np
import math
import copy

X = 5
Y = 3
T = 200
SERVICE_POLICY = "WRR"
PROCESSOR_NUMER = 3
LINE_LIMIT = 10

in_system_processes = dict()
finished_processes = dict()
time = 0
process_number = 1
next_process_in = -1
is_server_busy = False
server_free_in = -1
current_process_in_server = -1

processors_busy = [False for _ in range(PROCESSOR_NUMER)]
processors_free_in_time = [-1 for _ in range(PROCESSOR_NUMER)]
processes_in_server = [-1 for _ in range(PROCESSOR_NUMER)]
# from low to high
WRR_Lines = [[] for _ in range(3)]
WRR_Weights = [3, 2, 1]
Last_WRR_state = [3, 3]  # (priority, left)


def generate_random_time(service_type):
    param = X if service_type == "interarrival" else Y
    return math.ceil((-60 / param) * np.log(1 - random.random()))


def does_found_free_processor():
    for index, is_busy in enumerate(processors_busy):
        if not is_busy:
            return index
    return None


def find_processor_finish_in_time(time):
    all_found_processors = []
    for index, server_time in enumerate(processors_free_in_time):
        if server_time == time:
            all_found_processors.append(index)
    return all_found_processors


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
    # just escape the first process
    if process_number > 1:
        WRR_Lines[priority - 1].append(process_number)

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
    global is_server_busy, server_free_in
    all_found_Server = find_processor_finish_in_time(time)
    if len(all_found_Server):
        for found_server in all_found_Server:  # check all finished processes on processors
            server_id = found_server
            processors_busy[server_id] = False
            processors_free_in_time[server_id] = -1
            current_process_in_server = processes_in_server[server_id]
            in_system_processes[current_process_in_server]["out_server_time"] = time
            processes_in_server[server_id] = -1
            current_process = copy.deepcopy(in_system_processes[current_process_in_server])
            finished_processes[current_process_in_server] = current_process
            print(f"process number {current_process_in_server} released server: {server_id} in time: {time}")
            del in_system_processes[current_process_in_server]

    free_processor = does_found_free_processor()
    if len(in_system_processes) != 0 and free_processor != None:
        if SERVICE_POLICY == "FIFO":
            ids = in_system_processes.keys()
            # just check the Line limit
            if len(ids) <= LINE_LIMIT:
                current_id = min(ids)
                select_process(current_id, free_processor)

        elif SERVICE_POLICY == "WRR":
            get_next_process_WRR(free_processor)

        elif SERVICE_POLICY == "NPPS":
            ids = in_system_processes.keys()
            # just check the Line limit
            if len(ids) <= LINE_LIMIT:
                current_id = get_next_process_for_npps()
                select_process(current_id, free_processor)


def get_next_process_WRR(free_processor):
    global Last_WRR_state
    if Last_WRR_state[0] == 3 and Last_WRR_state[1] > 0:
        if len(WRR_Lines[2]) and len(WRR_Lines[2]) < LINE_LIMIT:
            Last_WRR_state = [3, Last_WRR_state[1] - 1]
            current_id = WRR_Lines[2].pop(0)
            select_process(current_id, free_processor)
            print(f"A process executed ftom line: 3")
        elif len(WRR_Lines[1]) and len(WRR_Lines[1]) < LINE_LIMIT:
            Last_WRR_state = [2, 1]
            current_id = WRR_Lines[1].pop(0)
            select_process(current_id, free_processor)
            print(f"A process executed ftom line: 2")
        elif len(WRR_Lines[0]) and len(WRR_Lines[0]) < LINE_LIMIT:
            Last_WRR_state = [1, 0]
            current_id = WRR_Lines[0].pop(0)
            select_process(current_id, free_processor)
            print(f"A process executed ftom line: 1")
        else:
            pass
    elif Last_WRR_state[0] == 2 and Last_WRR_state[1] > 0:
        if len(WRR_Lines[1]) and len(WRR_Lines[1]) < LINE_LIMIT:
            Last_WRR_state = [2, Last_WRR_state[1] - 1]
            current_id = WRR_Lines[1].pop(0)
            select_process(current_id, free_processor)
            print(f"A process executed ftom line: 2")
        elif len(WRR_Lines[0]) and len(WRR_Lines[0]) < LINE_LIMIT:
            Last_WRR_state = [1, 0]
            current_id = WRR_Lines[0].pop(0)
            select_process(current_id, free_processor)
            print(f"A process executed ftom line: 1")
        elif len(WRR_Lines[2]) and len(WRR_Lines[2]) < LINE_LIMIT:
            Last_WRR_state = [3, 2]
            current_id = WRR_Lines[2].pop(0)
            select_process(current_id, free_processor)
            print(f"A process executed ftom line: 3")
        else:
            pass
    elif Last_WRR_state[0] == 1 and Last_WRR_state[1] > 0:
        if len(WRR_Lines[2]) and len(WRR_Lines[2]) < LINE_LIMIT:
            Last_WRR_state = [3, 2]
            current_id = WRR_Lines[2].pop(0)
            select_process(current_id, free_processor)
            print(f"A process executed ftom line: 3")
        elif len(WRR_Lines[1]) and len(WRR_Lines[1]) < LINE_LIMIT:
            Last_WRR_state = [2, 1]
            current_id = WRR_Lines[1].pop(0)
            select_process(current_id, free_processor)
            print(f"A process executed ftom line: 2")
        elif len(WRR_Lines[0]) and len(WRR_Lines[0]) < LINE_LIMIT:
            Last_WRR_state = [1, Last_WRR_state[1] - 1]
            current_id = WRR_Lines[0].pop(0)
            select_process(current_id, free_processor)
            print(f"A process executed ftom line: 1")
        else:
            pass


def select_process(current_id, free_processor):
    global is_server_busy, server_free_in, current_process_in_server
    server_id = free_processor
    in_system_processes[current_id]["in_server_time"] = time
    processes_in_server[server_id] = current_id
    current_process = in_system_processes[current_id]
    current_process_in_server = current_id
    service_time = current_process["service_time"]
    processors_busy[server_id] = True
    server_free_in = time + service_time
    processors_free_in_time[server_id] = server_free_in
    print(
        f"process number {current_id} got server: {server_id} in time: {time} and will hold it for {service_time} seconds")


def start():
    global time, in_system_processes, process_number, next_process_in
    if time == 0:
        store_process()
        server_id = 0
        processors_free_in_time[server_id] = next_process_in
        processes_in_server[server_id] = 1
        process_number += 1
        processors_busy[server_id] = True
    while time <= T:
        generate_process()
        server()
        time += 1


if __name__ == '__main__':
    start()
