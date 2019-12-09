import xml.etree.ElementTree as et
from collections import Counter

path = '../data/'
files = ['BPIC15_1.xes', 'BPIC15_2.xes', 'BPIC15_3.xes', 'BPIC15_4.xes', 'BPIC15_5.xes']


def load_xes(file):
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
        for info in trace.findall('{http://www.xes-standard.org/}date'):
            if info.attrib['key'] == 'startDate':
                start = info.attrib['value']
            if info.attrib['key'] == 'endDate':
                end = info.attrib['value']

        for e in trace.iter('{http://www.xes-standard.org/}event'):

            event = {}

            for info in e:
                if info.attrib['key'] == 'org:resource':
                    event['resource'] = info.attrib['value']
                if info.attrib['key'] == 'time:timestamp':
                    event['start'] = info.attrib['value']
                if info.attrib['key'] == 'dateFinished':
                    event['end'] = info.attrib['value']
                if info.attrib['key'] == 'planned':
                    event['plannend'] = info.attrib['value']
                if info.attrib['key'] == 'activityNameEN':
                    event['activity'] = info.attrib['value']

            events.append(event)

        log[trace_id] = {
            'trace_id': trace_id,
            'start': start,
            'end': end,
            'municipality': file.split('.')[0],
            'events': events
        }

    return log


def preprocess(data, minOccurenceForActivity = 50):
    print('Start Preprocessing')

    def get_occurence():
        tasks = []
        for trace in data.keys():
            tasks += [event['activity'] for event in data[trace]['events']]
        return Counter(tasks)

    occurences1 = get_occurence()

    for t in occurences1:
        if occurences1[t] < minOccurenceForActivity:
            for trace in data.keys():
                for i in reversed(range(len(data[trace]['events']))):
                    if data[trace]['events'][i]['activity'] == t:
                        del data[trace]['events'][i]

    occurences2 = get_occurence()
    print('Removed ' + str(1 - len(list(occurences2.values())) / len(list(occurences1.values()))) + ' % of the unique activities')
    print('Removed ' + str(1 - sum(list(occurences2.values())) / sum(list(occurences1.values()))) + ' % of all activities')

    return data


def get_cases(data):
    cases = set()

    for trace in data.keys():
        cases.add(tuple([event['activity'] for event in data[trace]['events']]))

    return cases


if __name__ == '__main__':
    data = {}

    for file in files:
        data.update(load_xes(file))

    data = preprocess(data)
    cases = get_cases(data)
