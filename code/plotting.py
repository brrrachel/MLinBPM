import matplotlib.pyplot as plt
plt.rcParams["font.family"] = "Times New Roman"
import datetime
from dateutil.parser import parse


def occurrence_plotting(occurrences, threshold):
    values = sorted(list(occurrences.values()))
    plt.plot(range(len(values)), values)
    plt.xlabel('Activities')
    plt.ylabel('Occurences')
    plt.grid(True)
    plt.savefig('plots/occurences_' + str(threshold).split('.')[1] + '.pdf')


def duration_plotting(data, threshold):
    fig, ax = plt.subplots()

    index = 0
    for trace in data.keys():
        if type(data[trace]['start']) is str:
            start = parse(data[trace]['start'])
        else:
            start = data[trace]['start']
        duration = datetime.timedelta(hours=0, minutes=0, seconds=0)
        for event in data[trace]['events']:
            if type(event['duration']) is str:
                if ' days, ' in event['duration']:
                    days, timestamp = event['duration'].split(' days, ')
                elif ' day, ' in event['duration']:
                    days, timestamp = event['duration'].split(' day, ')
                t = datetime.datetime.strptime(timestamp, "%H:%M:%S") + datetime.timedelta(days=int(days))
                duration += datetime.timedelta(days=t.day, hours=t.hour, minutes=t.minute, seconds=t.second)
            else:
                duration += event['duration']

        ax.hlines(y=index, xmin=start, xmax=(start + duration))
        index+=1

    plt.xlabel('Time')
    plt.ylabel('Traces')
    ax.set_yticklabels([])
    plt.savefig('plots/duration_' + str(threshold).split('.')[1] + '.pdf')
