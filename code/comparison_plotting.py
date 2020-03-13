import matplotlib.pyplot as plt
from dateutil.parser import parse
import numpy as np
from tqdm import tqdm
import json
import datetime
from dataLoader import _load_preprocessed_data, limit_data
from utils import calculate_salaries, parse_timedelta

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


def _plot_overview(data):

    data_duration = []
    data_costs = []

    original_data = _load_preprocessed_data(0.0, 0.0)
    original_data = limit_data(original_data, datetime.datetime.strptime("2012/10/01", "%Y/%m/%d"), datetime.datetime.strptime("2012/11/15", "%Y/%m/%d"))
    salaries = calculate_salaries(original_data)

    # calculate duration and costs for the original log
    cost = 0
    duration = 0
    for trace_id in original_data.keys():
        trace = original_data[trace_id]
        for event in trace['events']:
            duration_in_seconds = parse_timedelta(event['duration']).total_seconds()
            cost += salaries[event['resource']]['salary'] / 3600 * duration_in_seconds
            duration += duration_in_seconds
    data_duration.append(duration / 3600 / 24)
    data_costs.append(cost / 1000)

    # calculate for each allocator duration and costs
    for allocator_key in tqdm(data.keys()):
        duration = 0
        cost = 0
        for trace_key in data[allocator_key].keys():
            if trace_key != 'workload':
                for activity in data[allocator_key][trace_key]:
                    cost_for_activity = activity['costs']
                    cost += cost_for_activity
                    duration += (parse(activity['end']) - parse(activity['start'])).total_seconds()
        data_duration.append(duration/3600/24)
        data_costs.append(cost / 1000)

    # create dataset labels for plot
    labels = ['Preprocessed Log'] + list(data.keys())
    x = np.arange(len(labels))

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
    plt.savefig("plots/comparison/results_comparison.pdf")


if __name__ == '__main__':

    # load all result files
    complete_data = dict()
    complete_data['Role-Based Allocator'] = _load_results('GreedyAllocator', '1', 0.0017, 0.005)
    complete_data['Q-Value Allocator'] = _load_results('QValueAllocator', '1', 0.0017, 0.005)
    complete_data['Multi-Objective Allocator'] = _load_results('QValueMultiDimensionAllocator', '1', 0.0017, 0.005)

    # start with plotting
    _plot_overview(complete_data)
