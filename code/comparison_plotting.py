import matplotlib.pyplot as plt
from dateutil.parser import parse
import numpy as np
from tqdm import tqdm
import json
import datetime
from dataLoader import _load_preprocessed_data, limit_data
from utils import calculate_salaries

plt.rcParams["font.family"] = "Times New Roman"
one_hour = datetime.timedelta(hours=1, minutes=0, seconds=0)
one_month = datetime.timedelta(days=30)


def _get_filename(allocator_name, workload, threshold, threshold_occurrence_in_traces):
    filename = 'results/' + str(threshold).split('.')[1] + "_" + str(threshold_occurrence_in_traces).split('.')[1] + '_' + allocator_name + '_w' + str(workload) + '.json'
    return filename


def _load_results(allocator_name, workload, threshold, threshold_occurrence_in_traces):
    try:
        with open(_get_filename(allocator_name, workload, threshold, threshold_occurrence_in_traces), 'r') as fp:
            return json.load(fp)
    except IOError:
        return False


def plot_costs(data):

    data_duration = []
    data_costs = []

    original_data = _load_preprocessed_data(0.0, 0.0)
    original_data = limit_data(original_data, datetime.datetime.strptime("2012/10/01", "%Y/%m/%d"), datetime.datetime.strptime("2012/11/15", "%Y/%m/%d"))
    salaries = calculate_salaries(original_data)

    cost = 0
    duration = 0
    for trace_id in original_data.keys():
        trace = original_data[trace_id]
        for event in trace['events']:
            event['duration'] = parse(event['end']) - parse(event['start'])
            if ('planned' in event) & (event['duration'] < one_hour):
                event['duration'] = parse(event['planned']) - parse(event['start'])
            if event['duration'] < one_hour:
                event['duration'] = one_hour
            if event['duration'] > one_month:
                event['duration'] = one_month

            cost += salaries[event['resource']]['salary'] / 3600 * event['duration'].total_seconds()
            duration += event['duration'].total_seconds()

    data_duration.append(duration / 3600 / 24)
    data_costs.append(cost / 1000)

    traces = set()
    print('plotting comparison of allocators')
    for trace in data[next(iter(data))]:
        if trace != 'workload':
            traces.add(trace)

    labels = ['Original Log'] + list(data.keys())
    x = np.arange(len(labels))

    for allocator_key in tqdm(data.keys()):

        duration = 0
        cost = 0

        for trace_key in data[allocator_key].keys():
            if trace_key != 'workload':
                for activity in data[allocator_key][trace_key]:
                    cost_for_activity = activity['costs']
                    cost += cost_for_activity
                    duration += (parse(activity['end']) - parse(activity['start'])).total_seconds()

        data_duration.append(duration/3600/24)  # save as min
        data_costs.append(cost / 1000)

    print(data_costs, data_duration)

    # Duration Plot
    plt.subplot(1, 2, 1)
    bar1 = plt.bar(x, data_duration, align='center', color="grey")
    for i in range(len(bar1)):
        heigth = bar1[i].get_height()
        plt.text(bar1[i].get_x() + bar1[i].get_width()/2, heigth, round(data_duration[i], 2), size=8, color='black', weight='bold', ha='center', va='bottom')
    plt.xticks(x, labels, rotation='vertical')
    plt.ylabel('Total Duration [days]')

    # Cost Plot
    plt.subplot(1, 2, 2)
    bar2 = plt.bar(x, data_costs, align='center', color='#DD640C')
    for i in range(len(bar2)):
        heigth = bar2[i].get_height()
        plt.text(bar2[i].get_x() + bar2[i].get_width()/2, heigth, round(data_costs[i], 2), size=8, color='black', weight='bold', ha='center', va='bottom')
    plt.xticks(x, labels, rotation='vertical')
    plt.ylabel('Total Costs in thousand')

    plt.tight_layout()

    plt.savefig("plots/cost/cost_comparison.png")


complete_data = dict()
complete_data['GreedyAllocator_w1'] = _load_results('GreedyAllocator', '1', 0.0017, 0.005)
#complete_data['GreedyAllocator_w3'] = _load_results('GreedyAllocator', '3', 0.0017, 0.005)
complete_data['QValueAllocator_w1'] = _load_results('QValueAllocator', '1', 0.0017, 0.005)
#complete_data['QValueAllocator_w3'] = _load_results('QValueAllocator', '1', 0.0017, 0.005)
complete_data['QValueMultiDimension_w1'] = _load_results('QValueMultiDimensionAllocator', '1', 0.0017, 0.005)
#complete_data['QValueMultiDimension_w3'] = _load_results('QValueMultiDimensionAllocator', '3', 0.0017, 0.005)

plot_costs(complete_data)
