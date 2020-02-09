import matplotlib.pyplot as plt
import numpy as np
from dateutil.parser import parse
from tqdm import tqdm
from utils import parse_timedelta, normalize_salary

plt.rcParams["font.family"] = "Times New Roman"


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


def legend_without_duplicate_labels(ax):
    handles, labels = ax.get_legend_handles_labels()
    unique = [(h, l) for i, (h, l) in enumerate(zip(handles, labels)) if l not in labels[:i]]
    ax.legend(*zip(*unique), loc="best")


def occurrence_plotting(occurrences, total_num_threshold, trace_num_threshold):
    values = sorted(list(occurrences.values()))
    plt.plot(range(len(values)), values)
    plt.xlabel('Activity ID')
    plt.ylabel('Occurences')
    plt.grid(True)
    plt.savefig('plots/activities/occurrences_' + str(total_num_threshold).split('.')[1] + '_' + str(trace_num_threshold).split('.')[1] + '.pdf')


def input_data_duration_plotting(data, threshold):
    filename = 'plots/inputDataDuration/' + str(threshold).split('.')[1] + '.pdf'
    fig, ax = plt.subplots()

    print("Plotting duration of traces in log")
    index = 0
    for trace in tqdm(data.keys()):
        for event in data[trace]['events']:
            start, duration = _get_start_duration(event)
            ax.hlines(y=trace, xmin=start, xmax=(start + duration))
        index += 1

    plt.xlabel('Time')
    plt.ylabel('Traces')
    plt.grid(True)
    plt.savefig(filename)


def allocation_duration_plotting(results, allocator, threshold):
    filename = 'plots/allocatingDuration/' + allocator + '_' + str(threshold).split('.')[1] + '.pdf'
    fig, ax = plt.subplots()

    resources = set()
    for trace in results.keys():
        if trace != 'workload':
            for activity in results[trace]:
                resources.add(str(activity['resource']))
    resources = list(resources)

    cmap = plt.get_cmap('jet')
    colors = [cmap(i) for i in np.linspace(0, 1, len(list(resources)))]

    print("plotting duration with new allocation")
    for trace in tqdm(results.keys()):
        if trace != 'workload':
            for activity in results[trace]:
                start, duration = _get_start_duration(activity)
                color_index = resources.index(activity['resource'])
                ax.hlines(y=trace, xmin=start, xmax=(start + duration), color=colors[color_index], label=activity['resource'])

    legend_without_duplicate_labels(ax)
    plt.xlabel('Time')
    plt.ylabel('Traces')
    ax.set_yticklabels([])
    fig.autofmt_xdate()
    plt.savefig(filename)


def resource_workload_plotting(results, allocator, threshold, trace_num_threshold):
    filename = 'plots/resources/' + allocator + '_' + str(threshold).split('.')[1] + str(trace_num_threshold).split('.')[1] + '.pdf'
    fig, ax = plt.subplots()

    resources = set()
    activities = set()

    for trace in results.keys():
        if trace != 'workload':
            for activity in results[trace]:
                resources.add(activity['resource'])
                activities.add(activity['activity'])
    resources = list(resources)
    activities = list(activities)

    cmap = plt.get_cmap('jet')
    colors = [cmap(i) for i in np.linspace(0, 1, len(list(activities)))]

    print("plotting workload of resources")
    for resource in tqdm(resources):
        for trace in results.keys():
            if trace != 'workload':
                for activity in results[trace]:
                    if activity['resource'] == resource:
                        start, duration = _get_start_duration(activity)
                        color_index = activities.index(activity['activity'])
                        ax.hlines(y=resource, xmin=start, xmax=(start + duration), color=colors[color_index], label=activity['activity'])

    legend_without_duplicate_labels(ax)
    plt.xlabel('Time')
    plt.ylabel('Resources')
    fig.autofmt_xdate()
    plt.savefig(filename)


def resource_distribution(table):
    activities = []
    resources = []
    for key in sorted(table.keys()):
        activities.append(key)
        resources_with_skill = [r[0] for r in table[key].items() if r[1] > 0]
        resources.append(len(resources_with_skill))

    x_pos = [i for i, _ in enumerate(activities)]
    plt.bar(x_pos, resources, color='green')

    plt.xlabel("Activities")
    plt.xticks(rotation=90)
    plt.ylabel("Number of Resources which have already executed this activity")

    plt.xticks(x_pos, activities)


def activity_occurence_histogram(occurences):
    fig, ax1 = plt.subplots()

    data = [occurences[key]['activities'] for key in occurences.keys()]
    bins = list(range(0, max(data), 1))
    ax1.hist(data, bins=bins, color="black", edgecolor="white", align='mid')
    ax1.set_xlabel("Number of different activities per resource")
    ax1.set_ylabel("Frequency")

    plt.savefig('plots/skills_distribution.pdf')


def input_data_duration_plotting(data,  threshold, trace_num_threshold):
    filename = 'plots/inputDataDuration/' + str(threshold).split('.')[1] + '_' + str(trace_num_threshold).split('.')[1] + '.pdf'
    fig, ax = plt.subplots()

    print("Plotting duration of traces in log")
    for trace in tqdm(data.keys()):
        if trace != 'workload':
            for event in data[trace]['events']:
                start, duration = _get_start_duration(event)
                ax.hlines(y=trace, xmin=start, xmax=(start + duration))

    plt.xticks(rotation=45)
    ax.set(xlabel='Time', ylabel='Trace ID',
           title='Original Duration For Each Trace')
    plt.grid(True)
    fig.autofmt_xdate()
    plt.tight_layout()
    fig.savefig(filename)


def trace_duration_plotting(data, allocator, threshold, trace_num_threshold, workload):
    filename = 'plots/inputDataDuration/' + allocator + '_w' + str(workload) + '_' + str(threshold).split('.')[1] + '_' + str(trace_num_threshold).split('.')[1] + '.pdf'
    fig, ax = plt.subplots()

    print("Plotting duration of traces in log")
    for trace in tqdm(data.keys()):
        if trace != 'workload':
            for event in data[trace]:
                start, duration = _get_start_duration(event)
                ax.hlines(y=trace, xmin=start, xmax=(start + duration))

    plt.xticks(rotation=45)
    ax.set(xlabel='Time', ylabel='Trace ID',
           title='Duration for each trace using ' + allocator + ' with a workload of ' + str(workload))
    plt.grid(True)
    fig.autofmt_xdate()
    plt.tight_layout()
    fig.savefig(filename)


def plot_workload(workloads, threshold, trace_num_threshold, workload, allocator_name):
    timestamps = []
    busy_resources = []
    print('plotting workload')
    for key in workloads.keys():
        if parse(key).second != 30:
            timestamps.append(parse(key))
            busy_resources.append(workloads[key])

    fig, ax = plt.subplots()
    plt.yticks(np.arange(min(busy_resources), max(busy_resources)+1, 2.0))
    ax.plot(timestamps, busy_resources)

    ax.set(xlabel='time', ylabel='number of busy resources',
           title='Number of busy resources using allocator ' + allocator_name + ' with a workload of ' + str(workload))
    plt.xticks(rotation=45)
    ax.grid()
    fig.autofmt_xdate()

    fig.savefig("plots/workload/" + allocator_name + '_w' + str(workload) + '_' + str(threshold).split('.')[1] + '_' + str(trace_num_threshold).split('.')[1] + ".pdf")
