import matplotlib.pyplot as plt
plt.rcParams["font.family"] = "Times New Roman"
import datetime
from dateutil.parser import parse


def occurrence_plotting(occurrences):
    values = sorted(list(occurrences.values()))
    plt.plot(range(len(values)), values)
    plt.xlabel('Activities')
    plt.ylabel('Occurences')
    plt.grid(True)
    plt.savefig('plots/occurences.pdf')


def duration_plotting(data):
    fig, ax = plt.subplots()

    index = 0
    for trace in data.keys():
        start = parse(data[trace]['start'])
        end = datetime.timedelta(hours=0, minutes=0, seconds=0)
        for event in data[trace]['events']:
            if ' days, ' in event['duration']:
                days, timestamp = event['duration'].split(' days, ')
            elif ' day, ' in event['duration']:
                days, timestamp = event['duration'].split(' day, ')
            t = datetime.datetime.strptime(timestamp, "%H:%M:%S") + datetime.timedelta(days=int(days))
            delta = datetime.timedelta(days=t.day, hours=t.hour, minutes=t.minute, seconds=t.second)
            end += delta

        ax.hlines(y=index, xmin=start, xmax=(start + end))
        index+=1

    plt.xlabel('Time')
    plt.ylabel('Traces')
    ax.set_yticklabels([])
    plt.savefig('plots/duration.pdf')
