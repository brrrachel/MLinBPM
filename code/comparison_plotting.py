import matplotlib.pyplot as plt
import matplotlib
import numpy as np
from tqdm import tqdm
import json


def _get_filename(allocator_name, workload, threshold, threshold_occurrence_in_traces):
    filename = 'results/' + str(threshold).split('.')[1] + "_" + str(threshold_occurrence_in_traces).split('.')[1] + '_' + allocator_name + '_w' + str(workload) + '.json'
    return filename


def _load_preprocessed_data(allocator_name, workload, threshold, threshold_occurrence_in_traces):
    try:
        with open(_get_filename(allocator_name, workload, threshold, threshold_occurrence_in_traces), 'r') as fp:
            return json.load(fp)
    except IOError:
        return False


def plot_costs(data):

    fig, ax = plt.subplots()
    width = 0.35  # the width of the bars
    x = None
    traces = set()
    print('plotting workload')
    for trace in data[next(iter(data))]:
        if trace != 'workload':
            traces.add(trace)
    x = np.arange(len(traces))

    index = -1

    for allocator_key in data.keys():
        allocator_data = data[allocator_key]
        complete_costs = []
        for trace_key in tqdm(traces):
            trace = allocator_data[trace_key]
            cost = 0
            for activity in trace:
                cost_for_activity = activity['costs']
                cost += cost_for_activity
            complete_costs.append(cost)
        ax.bar(x + (index * width), complete_costs, width, label=allocator_key)
        index += 1

    # Add some text for labels, title and custom x-axis tick labels, etc.
    ax.set(xlabel='Trace ID', ylabel='Cost',
           title='Costs per trace')

    ax.set_xticks(x)
    plt.xticks(rotation=45)
    print(traces)
    ax.set_xticklabels(traces)
    ax.legend()

    fig.tight_layout()

    fig.savefig("plots/cost/cost_comparison.png")


complete_data = {}

greedy_w1 = _load_preprocessed_data('GreedyAllocator', '1', 0.0017, 0.005)
greedy_w3 = _load_preprocessed_data('GreedyAllocator', '3', 0.0017, 0.005)
q_value_w1 = _load_preprocessed_data('QValueAllocator', '1', 0.0017, 0.005)
q_value_w3 = _load_preprocessed_data('QValueAllocator', '1', 0.0017, 0.005)

complete_data['GreedyAllocator_w1'] = greedy_w1
# complete_data['GreedyAllocator_w3'] = greedy_w3
complete_data['QValueAllocator_w1'] = q_value_w1
# complete_data['QValueAllocator_w3'] = q_value_w3

plot_costs(complete_data)
