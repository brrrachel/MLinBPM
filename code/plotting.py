import matplotlib.pyplot as plt
import numpy as np
import datetime
from dateutil.parser import parse
from tqdm import tqdm

plt.rcParams["font.family"] = "Times New Roman"


def _get_start_duration(activity):
    start = None
    duration = None
    if type(activity['start']) is str:
        start = parse(activity['start'])
    else:
        start = activity['start']

    if type(activity['duration']) is str:
        days = None
        timestamp = None
        if ' days, ' in activity['duration']:
            days, timestamp = activity['duration'].split(' days, ')
        elif ' day, ' in activity['duration']:
            days, timestamp = activity['duration'].split(' day, ')
        else:
            days = 0
            timestamp = activity['duration']
        t = datetime.datetime.strptime(timestamp, "%H:%M:%S") + datetime.timedelta(days=int(days))
        duration = datetime.timedelta(days=t.day, hours=t.hour, minutes=t.minute, seconds=t.second)
    else:
        duration = activity['duration']
    return start, duration


def legend_without_duplicate_labels(ax):
    handles, labels = ax.get_legend_handles_labels()
    unique = [(h, l) for i, (h, l) in enumerate(zip(handles, labels)) if l not in labels[:i]]
    ax.legend(*zip(*unique), loc="best")


def occurrence_plotting(occurrences, threshold):
    values = sorted(list(occurrences.values()))
    plt.plot(range(len(values)), values)
    plt.xlabel('Activities')
    plt.ylabel('Occurences')
    plt.grid(True)
    plt.savefig('plots/occurences_' + str(threshold).split('.')[1] + '.pdf')


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
        for activity in results[trace]:
            resources.add(activity['resource'])
    resources = list(resources)

    cmap = plt.get_cmap('jet')
    colors = [cmap(i) for i in np.linspace(0, 1, len(list(resources)))]

    print("plotting duration with new allocation")
    for trace in tqdm(results.keys()):
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


def resource_workload_plotting(results, allocator, threshold):
    filename = 'plots/resources/' + allocator + '_' + str(threshold).split('.')[1] + '.pdf'
    fig, ax = plt.subplots()

    resources = set()
    activities = set()

    for trace in results.keys():
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
