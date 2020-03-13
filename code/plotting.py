import matplotlib.pyplot as plt
import numpy as np
from dateutil.parser import parse
from tqdm import tqdm
from utils import parse_timedelta, normalize_salary

plt.rcParams["font.family"] = "Times New Roman"


def _plot_already_available(filename):
    try:
        with open(filename, 'r') as fp:
            return True
    except IOError:
        return False


def _get_start_duration(activity):
    start = None
    duration = None
    if type(activity['start']) is str:
        start = parse(activity['start'])
    else:
        start = activity['start']

    if type(activity['duration']) is str:
        duration = parse_timedelta(activity['duration'])
    else:
        duration = activity['duration']
    return start, duration


def _legend_without_duplicate_labels(ax):
    handles, labels = ax.get_legend_handles_labels()
    unique = [(h, l) for i, (h, l) in enumerate(zip(handles, labels)) if l not in labels[:i]]
    ax.legend(*zip(*unique), loc="best")


def activity_occurrence_plotting(occurrences, total_num_threshold, trace_num_threshold):
    # plots how often a activity occures in the dataset
    filename = 'plots/activities/occurrences_' + str(total_num_threshold).split('.')[1] + '_' + str(trace_num_threshold).split('.')[1] + '.pdf'

    if not _plot_already_available(filename):
        values = sorted(list(occurrences.values()))
        plt.plot(range(len(values)), values)
        plt.xlabel('Activity ID')
        plt.ylabel('Occurences')
        plt.grid(True)
        plt.savefig(filename)


def skills_distribution_plotting(occurences):
    # plots the number of different activities per resource
    filename = 'plots/activities/skills_distribution.pdf'
    fig, ax1 = plt.subplots()

    if not _plot_already_available(filename):
        data = [occurences[key]['activities'] for key in occurences.keys()]
        bins = list(range(0, max(data), 1))
        ax1.hist(data, bins=bins, color="black", edgecolor="white", align='mid')
        ax1.set_xlabel("Number of different activities per resource")
        ax1.set_ylabel("Frequency")
        plt.savefig(filename)


def input_data_duration_plotting(data):
    # takes the input data and plots for each trace the duration in time
    # good for comparison with plot from allocation_trace_duration_plotting
    filename = 'plots/duration/inputDataDuration.png'
    fig, ax = plt.subplots()

    if not _plot_already_available(filename):
        print("Plotting original duration of traces in log")
        for trace in tqdm(data.keys()):
            if trace != 'workload':
                for event in data[trace]['events']:
                    start, duration = _get_start_duration(event)
                    ax.hlines(y=trace, xmin=start, xmax=(start + duration))

        plt.xticks(rotation=45)
        ax.set(xlabel='Time', ylabel='Trace ID',
               title='Original duration for each trace')
        plt.grid(True)
        fig.autofmt_xdate()
        plt.tight_layout()
        fig.savefig(filename)


def allocation_trace_duration_plotting(data, allocator, total_num_threshold, trace_num_threshold, workload):
    # takes the the log data from the allocation and visualize for each trace the duration in time
    # good for comparison with plot from input_data_duration_plotting
    filename = 'plots/duration/' + allocator + '_w' + str(workload) + '_' + str(total_num_threshold).split('.')[1] + '_' + str(trace_num_threshold).split('.')[1] + '.pdf'
    fig, ax = plt.subplots()

    if not _plot_already_available(filename):
        print("Plotting duration of traces from the allocation")
        for trace in tqdm(data.keys()):
            if trace != 'workload':
                for event in data[trace]:
                    start, duration = _get_start_duration(event)
                    ax.hlines(y=trace, xmin=start, xmax=(start + duration), colors="brown")

        plt.xticks(rotation=45)
        ax.set(xlabel='Time', ylabel='Traces')
        ax.set_yticklabels([])
        plt.grid(True)
        fig.autofmt_xdate()
        plt.tight_layout()
        fig.savefig(filename)


def overall_workload_plotting(workloads, total_num_threshold, trace_num_threshold, workload, allocator_name):
    # plots the number of busy resources per each time interval
    filename = "plots/workload/" + allocator_name + '_w' + str(workload) + '_' + str(total_num_threshold).split('.')[1] + '_' + str(trace_num_threshold).split('.')[1] + ".pdf"
    timestamps = []
    busy_resources = []

    if not _plot_already_available(filename):
        print('Plotting overall workload')
        for key in workloads.keys():
            if parse(key).second != 30:
                timestamps.append(parse(key))
                busy_resources.append(workloads[key])

        fig, ax = plt.subplots()
        plt.yticks(np.arange(min(busy_resources), max(busy_resources)+1, 2.0))
        ax.plot(timestamps, busy_resources, color='brown')

        ax.set(xlabel='time', ylabel='number of busy resources')
        plt.xticks(rotation=45)
        ax.grid()
        fig.autofmt_xdate()
        fig.savefig(filename)
