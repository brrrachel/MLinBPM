import matplotlib.pyplot as plt
from dateutil.parser import parse
import numpy as np
from tqdm import tqdm
import json

plt.rcParams["font.family"] = "Times New Roman"


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

    traces = set()
    print('plotting comparison of allocators')
    for trace in data[next(iter(data))]:
        if trace != 'workload':
            traces.add(trace)

    labels = data.keys()
    x = np.arange(len(data.keys()))

    data_duration = []
    data_costs = []

    for allocator_key in tqdm(data.keys()):

        earliest_start = None
        latest_end = None
        cost = 0

        for trace_key in data[allocator_key].keys():
            if trace_key != 'workload':
                for activity in data[allocator_key][trace_key]:
                    cost_for_activity = activity['costs']
                    cost += cost_for_activity
                    if (earliest_start is None) or parse(activity['start']) < earliest_start:
                        earliest_start = parse(activity['start'])
                    if (latest_end is None) or (parse(activity['end']) > latest_end):
                        latest_end = parse(activity['end'])
        data_duration.append(((latest_end - earliest_start).total_seconds()/3600)/24)  # save as days
        data_costs.append(cost)

    # Duration Plot
    plt.subplot(1, 2, 1)
    plt.bar(x, data_duration, align='center', color="grey")
    plt.xticks(x, labels, rotation='vertical')
    plt.ylabel('Total Duration [days]')

    # Cost Plot
    plt.subplot(1, 2, 2)
    plt.bar(x, data_costs, align='center', color='#DD640C')
    plt.xticks(x, labels, rotation='vertical')
    plt.ylabel('Total Costs')

    plt.tight_layout()

    plt.savefig("plots/cost/cost_comparison.png")


complete_data = dict()
complete_data['GreedyAllocator_w1'] = _load_preprocessed_data('GreedyAllocator', '1', 0.0017, 0.005)
#complete_data['GreedyAllocator_w3'] = _load_preprocessed_data('GreedyAllocator', '3', 0.0017, 0.005)
complete_data['QValueAllocator_w1'] = _load_preprocessed_data('QValueAllocator', '1', 0.0017, 0.005)
#complete_data['QValueAllocator_w3'] = _load_preprocessed_data('QValueAllocator', '1', 0.0017, 0.005)
complete_data['QValueMultiDimension_w1'] = _load_preprocessed_data('QValueMultiDimensionAllocator', '1', 0.0017, 0.005)
#complete_data['QValueMultiDimension_w3'] = _load_preprocessed_data('QValueMultiDimensionAllocator', '3', 0.0017, 0.005)

plot_costs(complete_data)
