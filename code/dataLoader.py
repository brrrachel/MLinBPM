import xml.etree.ElementTree as et
import datetime
from collections import Counter
from dateutil.parser import parse

path = '../data/'
files = ['BPIC15_1.xes'] #, 'BPIC15_2.xes', 'BPIC15_3.xes', 'BPIC15_4.xes', 'BPIC15_5.xes']
one_second = datetime.timedelta(hours=0, minutes=0, seconds=1)


def _load_xes(file):
    print('Loading file ', file)
    log = {}

    tree = et.parse(path + file)
    data = tree.getroot()

    for trace in data.findall('{http://www.xes-standard.org/}trace'):

        trace_id = ''
        start = ''
        end = ''
        events = []

        for info in trace.findall('{http://www.xes-standard.org/}string'):
            if info.attrib['key'] == 'concept:name':
                trace_id = info.attrib['value']
                break
        for info in trace.findall('{http://www.xes-standard.org/}date'):
            if info.attrib['key'] == 'startDate':
                start = parse(info.attrib['value']).replace(tzinfo=None)
            if info.attrib['key'] == 'endDate':
                end = parse(info.attrib['value']).replace(tzinfo=None)

        last_end = start
        for e in trace.iter('{http://www.xes-standard.org/}event'):
            event = {}

            for info in e:
                #print(info.attrib['key'])
                if info.attrib['key'] == 'org:resource':
                    event['resource'] = info.attrib['value']
                if info.attrib['key'] == 'time:timestamp':
                    event['start'] = parse(info.attrib['value']).replace(tzinfo=None)
                if info.attrib['key'] == 'dateFinished':
                    event['end'] = parse(info.attrib['value']).replace(tzinfo=None)
                if info.attrib['key'] == 'planned':
                    event['planned'] = parse(info.attrib['value']).replace(tzinfo=None)
                if info.attrib['key'] == 'activityNameEN':
                    event['activity'] = info.attrib['value']

            event['duration'] = event['end'] - event['start']
            if event['duration'] < one_second:
                event['duration'] = event['end'] - last_end
            if ('planned' in event) & (event['duration'] < one_second):
                event['duration'] = event['planned'] - event['start']
            if event['duration'] < one_second:
                event['duration'] = datetime.timedelta(hours=0, minutes=0, seconds=0)
            last_end = event['end']
            # INFO: planned is not useful because sometimes planned or end is before start

            events.append(event)
        log[trace_id] = {
            'trace_id': trace_id,
            'start': start,
            'end': end,
            'municipality': file.split('.')[0],
            'events': events
        }

    return log


def load_data():
    data = {}
    for file in files:
        data.update(_load_xes(file))
    return data


def preprocess(data, occurenceThreshold = 0.3):
    print('Start Preprocessing')

    def get_occurence():
        tasks = []
        for trace in data.keys():
            tasks += [event['activity'] for event in data[trace]['events']]
        return Counter(tasks)

    occurences_before = get_occurence()

    for t in occurences_before:
        occurence_of_activity = occurences_before[t] / sum(list(occurences_before.values()))
        if occurence_of_activity / occurenceThreshold:
            for trace in data.keys():
                for i in reversed(range(len(data[trace]['events']))):
                    if data[trace]['events'][i]['activity'] == t:
                        del data[trace]['events'][i]

    occurences_after = get_occurence()
    print('Removed ' + str(1 - len(list(occurences_after.values())) / len(list(occurences_before.values()))) + ' % of the unique activities')
    print('Removed ' + str(1 - sum(list(occurences_after.values())) / sum(list(occurences_before.values()))) + ' % of all activities')

    return data
