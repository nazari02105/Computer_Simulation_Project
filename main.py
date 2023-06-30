import random
import numpy as np
import math
import copy
import matplotlib.pyplot as plt

X = 5
Y = 3
T = 1000
SERVICE_POLICY = "WRR"
PROCESSOR_NUMER = 3
LINE_LIMIT = 3

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

# FIFO and NPPS Line
fifo_npps_line = []

# WRR Line
# from low to high
WRR_Lines = [[] for _ in range(3)]
WRR_Weights = [3, 2, 1]
Last_WRR_state = [3, 3]  # (priority, left)

# for metrics
fifo_npps_line_length = []
wrr_line_length = []
total_number_of_drops = 0


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
    global next_process_in, process_number, total_number_of_drops
    interarrival = generate_random_time("interarrival")
    service_time = generate_random_time("service")
    priority = generate_priority()
    in_system_processes[process_number] = {"arrival_time": time, "service_time": service_time, "priority": priority}
    # add a process to its line
    # just escape the first process
    if process_number > 1:
        # just line length check
        if ((SERVICE_POLICY == "WRR" and len(WRR_Lines[priority - 1]) >= LINE_LIMIT)
                or (SERVICE_POLICY != "WRR" and len(fifo_npps_line) >= LINE_LIMIT)):
            print(f"Line is full!")
            total_number_of_drops += 1
        else:
            WRR_Lines[priority - 1].append(process_number)
            fifo_npps_line.append(
                [process_number, {"arrival_time": time, "service_time": service_time, "priority": priority}])

    print(f"process number {process_number} was added with arrival time = {time}, "
          f"service time = {service_time} and priority = {priority}.")
    print(f"next process will be in system {interarrival} seconds later.")
    process_number += 1
    next_process_in = time + interarrival


def get_next_process_for_npps(fifo_npps_line):
    max_priority = -1
    for detail in fifo_npps_line:
        if detail[1]["priority"] > max_priority:
            max_priority = detail[1]["priority"]
    least_time = math.inf
    for detail in fifo_npps_line:
        if detail[1]["priority"] == max_priority and detail[1]["arrival_time"] < least_time:
            least_time = detail[1]["arrival_time"]
    to_return = None
    for index, detail in enumerate(fifo_npps_line):
        if detail[1]["priority"] == max_priority and detail[1]["arrival_time"] == least_time:
            to_return = detail[0]
            fifo_npps_line.pop(index)
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
        if SERVICE_POLICY == "FIFO" and len(fifo_npps_line) > 0:
            current_id = fifo_npps_line.pop(0)[0]
            select_process(current_id, free_processor)

        elif SERVICE_POLICY == "WRR":
            get_next_process_WRR(free_processor)

        elif SERVICE_POLICY == "NPPS" and len(fifo_npps_line) > 0:
            current_id = get_next_process_for_npps(fifo_npps_line)
            if current_id != 1:
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
    in_system_processes[current_id]["server_id"] = server_id
    processes_in_server[server_id] = current_id
    current_process = in_system_processes[current_id]
    current_process_in_server = current_id
    service_time = current_process["service_time"]
    processors_busy[server_id] = True
    server_free_in = time + service_time
    processors_free_in_time[server_id] = server_free_in
    print(
        f"process number {current_id} got server: {server_id} in time: {time} and will hold it for {service_time} seconds")


def print_metrics():
    if SERVICE_POLICY == "WRR":
        first_line = []
        second_line = []
        third_line = []
        for tup in wrr_line_length:
            first_line.append(tup[0])
            second_line.append(tup[1])
            third_line.append(tup[2])
        first_mean = sum(first_line) / (len(first_line) + 1e-10)
        second_mean = sum(second_line) / (len(second_line) + 1e-10)
        third_mean = sum(third_line) / (len(third_line) + 1e-10)
        print("Average length of first line:", first_mean)
        print("Average length of second line:", second_mean)
        print("Average length of third line:", third_mean)
        print("Total Average length:", first_mean + second_mean + third_mean)

        first_line = []
        second_line = []
        third_line = []
        for key in finished_processes.keys():
            obj = finished_processes[key]
            if obj["priority"] == 1:
                first_line.append(obj["in_server_time"] - obj["arrival_time"])
            if obj["priority"] == 2:
                second_line.append(obj["in_server_time"] - obj["arrival_time"])
            if obj["priority"] == 3:
                third_line.append(obj["in_server_time"] - obj["arrival_time"])
        first_mean = sum(first_line) / (len(first_line) + 1e-10)
        second_mean = sum(second_line) / (len(second_line) + 1e-10)
        third_mean = sum(third_line) / (len(third_line) + 1e-10)
        print("Average wait time in first line:", first_mean)
        print("Average wait time in second line:", second_mean)
        print("Average wait time in third line:", third_mean)
        print("Total Average wait time:", first_mean + second_mean + third_mean)

        third_line = []
        for key in finished_processes.keys():
            obj = finished_processes[key]
            if obj["priority"] == 3:
                third_line.append(obj["in_server_time"] - obj["arrival_time"])
        if len(third_line) != 0:
            plot_cdf(third_line)
    else:
        print("Average length of line:", sum(fifo_npps_line_length) / (len(fifo_npps_line_length) + 1e-10))

        wait_time_list = []
        for key in finished_processes.keys():
            wait_time_list.append(finished_processes[key]["in_server_time"] - finished_processes[key]["arrival_time"])
        print("Average wait time in line:", sum(wait_time_list) / (len(wait_time_list) + 1e-10))

        wait_time_list = []
        for key in finished_processes.keys():
            obj = finished_processes[key]
            if obj["priority"] == 3:
                wait_time_list.append(obj["in_server_time"] - obj["arrival_time"])
        if len(wait_time_list) != 0:
            plot_cdf(wait_time_list)

    working_time = [0 for _ in range(PROCESSOR_NUMER)]
    for key in finished_processes.keys():
        obj = finished_processes[key]
        working_time[obj["server_id"]] += obj["service_time"]
    for i in range(len(working_time)):
        print(f"Utilization of server with id = {i} is {working_time[i] / T}")

    print("Total number of packet drops:", total_number_of_drops)


def store_metrics():
    if SERVICE_POLICY == "WRR":
        wrr_line_length.append((len(WRR_Lines[0]), len(WRR_Lines[1]), len(WRR_Lines[2])))
    else:
        fifo_npps_line_length.append(len(fifo_npps_line))


def plot_cdf(the_list):
    sorted_list = sorted(the_list)
    max_value = max(sorted_list) + 1
    x_axis = list(range(max_value))
    y_axis = [0 for _ in range(max_value)]
    for value in sorted_list:
        y_axis[value] += 1
    y_axis_main = list()
    for i in range(len(y_axis)):
        y_axis_main.append(sum(y_axis[:i + 1]))
    max_value = max(y_axis_main)
    for i in range(len(y_axis_main)):
        y_axis_main[i] = y_axis_main[i] / max_value
    plt.plot(x_axis, y_axis_main)
    plt.xlabel("wait time")
    plt.ylabel("cdf value")
    plt.title("CDF of wait time for high priority packets")
    plt.savefig('cdf.pdf')


def start():
    global time, in_system_processes, process_number, next_process_in
    if time == 0:
        global next_process_in, process_number
        interarrival = generate_random_time("interarrival")
        service_time = generate_random_time("service")
        priority = generate_priority()
        in_system_processes[process_number] = {"arrival_time": time, "service_time": service_time, "priority": priority,
                                               "in_server_time": 0, "server_id": 0}
        print(f"process number {process_number} was added with arrival time = {time}, "
              f"service time = {service_time} and priority = {priority}.")
        print(f"next process will be in system {interarrival} seconds later.")
        process_number += 1
        next_process_in = time + interarrival

        server_id = 0
        processors_free_in_time[server_id] = service_time
        processes_in_server[server_id] = 1
        processors_busy[server_id] = True
    while time <= T:
        generate_process()
        server()
        store_metrics()
        time += 1

    print("-" * 30)
    print_metrics()


if __name__ == '__main__':
    start()
