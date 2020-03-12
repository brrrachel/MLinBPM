import xml.etree.ElementTree as et
import datetime
import json
from collections import Counter
from plotting import input_data_duration_plotting, activity_occurrence_plotting
from dateutil.parser import parse
from operator import getitem

path = '../data/'
files = ['BPIC15_1.xes', 'BPIC15_2.xes', 'BPIC15_3.xes', 'BPIC15_4.xes', 'BPIC15_5.xes']
one_hour = datetime.timedelta(hours=1, minutes=0, seconds=0)
one_month = datetime.timedelta(days=30)


def _load_xes(file):
    log = {}

    tree = et.parse(path + file)
    data = tree.getroot()

    total_duration = []

    for trace in data.findall('{http://www.xes-standard.org/}trace'):

        trace_id = ''
        events = []

        for info in trace.findall('{http://www.xes-standard.org/}string'):
            if info.attrib['key'] == 'concept:name':
                trace_id = info.attrib['value']
                break

        last_end = None
        for e in trace.iter('{http://www.xes-standard.org/}event'):
            event = {}

            for info in e:
                if info.attrib['key'] == 'org:resource':
                    event['resource'] = info.attrib['value']
                if info.attrib['key'] == 'time:timestamp':
                    event['start'] = parse(info.attrib['value']).replace(tzinfo=None)
                    if last_end is None:
                        last_end = event['start']
                if info.attrib['key'] == 'dateFinished':
                    event['end'] = parse(info.attrib['value']).replace(tzinfo=None)
                if info.attrib['key'] == 'planned':
                    event['planned'] = parse(info.attrib['value']).replace(tzinfo=None)
                if info.attrib['key'] == 'activityNameEN':
                    event['activity'] = info.attrib['value']

            event['status'] = 'free'

            # calculate durations
            event['duration'] = event['end'] - event['start']
            if event['duration'] < one_hour:
                event['duration'] = event['end'] - last_end
            if ('planned' in event) & (event['duration'] < one_hour):
                event['duration'] = event['planned'] - event['start']
            if event['duration'] < one_hour:
                event['duration'] = one_hour
            if event['duration'] > one_month:
                event['duration'] = one_month
            last_end = event['end']

            total_duration.append((event['duration']).total_seconds())
            events.append(event)

        sorted_events = sorted(events, key=lambda e: e['start'])
        log[trace_id] = {
            'trace_id': trace_id,
            'start': sorted_events[0]['start'],
            'end': sorted_events[-1]['end'],
            'municipality': file.split('.')[0],
            'events': sorted_events
        }

    return log


def _get_filename(threshold, threshold_occurrence_in_traces):
    return path + 'preprocessed/preprocessed_' + str(threshold).split('.')[1] + "_" + str(threshold_occurrence_in_traces).split('.')[1] + '.json'


def _load_preprocessed_data(threshold, threshold_occurrence_in_traces):
    try:
        with open(_get_filename(threshold, threshold_occurrence_in_traces), 'r') as fp:
            return json.load(fp)
    except IOError:
        return False


def _safe_data(data, threshold, threshold_occurrence_in_traces):
    def converter(o):
        if isinstance(o, datetime.datetime) or isinstance(o, datetime.timedelta):
            return o.__str__()
    data = dict(sorted(data.items(), key=lambda x: getitem(x[1], 'start')))
    with open(_get_filename(threshold, threshold_occurrence_in_traces), 'w') as fp:
        json.dump(data, fp, default=converter)


def _get_occurrence(data):
    # calculates for each activity how often it has been executed over the whole log
    activity_instances = []
    occurrence_in_traces = {}
    for trace in data.keys():
        activity_instances_of_trace = []

        # collects for the trace the activity instances
        for event in data[trace]['events']:
            activity_instances_of_trace += [event['activity']]
            activity_instances += [event['activity']]

        # creates a dict for a trace each where the number of occurrences for each activity is saved
        activitiy_of_trace = set(activity_instances_of_trace)
        for a in activitiy_of_trace:
            if a not in occurrence_in_traces.keys():
                occurrence_in_traces[a] = 0
            occurrence_in_traces[a] += 1

    # returns the overall activity occurrence and a dict for each trace with the occurrences
    return Counter(activity_instances), occurrence_in_traces


def preprocess(data, total_num_threshold, trace_num_threshold):
    print('Start preprocess')
    preprocessed_data = {}

    occurrences_before, occurrences_in_traces = _get_occurrence(data)

    # calculate the min occurrence value
    min_occurrence_total = sum(list(occurrences_before.values())) * total_num_threshold
    min_occurrence_in_traces = sum(list(occurrences_before.values())) * trace_num_threshold

    # collect all activites which occure less then a threshold (min_occurrence_total or min_occurrence_in_traces)
    activities_to_delete = []
    for t in occurrences_before.keys():
        if occurrences_before[t] < min_occurrence_total:
            activities_to_delete.append(t)
    for t in occurrences_in_traces.keys():
        if occurrences_in_traces[t] < min_occurrence_in_traces:
            activities_to_delete.append(t)

    activities_to_delete_unique = set(activities_to_delete)

    for trace in data.keys():
        start = parse(data[trace]['start'])

        # for dropping outlines, we consider always only a certain timerange
        if datetime.datetime(year=2010, month=7, day=1) < start < datetime.datetime(year=2015, month=2, day=15):
            preprocessed_data[trace] = data[trace].copy()
            preprocessed_data[trace]['events'] = []
            for event in data[trace]['events']:

                # remain only activity instances which should not to be discarded
                if event['activity'] not in activities_to_delete_unique:
                    preprocessed_data[trace]['events'].append(event.copy())

            # if no activity instances are left in trace, discard the whole trace
            if len(preprocessed_data[trace]['events']) == 0:
                preprocessed_data.pop(trace)

    occurrences_after, occurrences_in_traces_after = _get_occurrence(preprocessed_data)
    activity_occurrence_plotting(occurrences_after, total_num_threshold, trace_num_threshold)

    print('Removed ' + str((1 - len(list(occurrences_after.values())) / len(list(occurrences_before.values()))) * 100) + ' % of the unique activities')
    print('Removed ' + str((1 - sum(list(occurrences_after.values())) / sum(list(occurrences_before.values()))) * 100) + ' % of all activities')

    if len(list(occurrences_after.values())) == 0:
        print('Threshold is too high, no activities left.')
        exit(0)

    return preprocessed_data


def limit_data(data, start, end):
    print('Limiting Data to ' + start.__str__() + ' and ' + end.__str__())
    limited_data = {}
    for trace in data.keys():
        # check for each trace wether start and end is within the selected time range
        trace_start = parse(data[trace]['start'])
        trace_end = parse(data[trace]['events'][-1]['end'])
        if (start <= trace_start) and (trace_end < end):
            limited_data[trace] = data[trace]

    if len(limited_data.keys()) == 0:
        print('No data available.')
        exit(0)
    return limited_data


def load_data(threshold_total, threshold_occurrence_in_traces):

    original_data = _load_preprocessed_data(0.0, 0.0)
    if not original_data:
        original_data = {}

        print('Data loading ...')
        for file in files:
            original_data.update(_load_xes(file))

        _safe_data(original_data, 0.0, 0.0)
        original_data = _load_preprocessed_data(0.0, 0.0)

    input_data_duration_plotting(original_data)

    preprocessed_data = _load_preprocessed_data(threshold_total, threshold_occurrence_in_traces)
    if not preprocessed_data:
        preprocessed_data = preprocess(original_data, threshold_total, threshold_occurrence_in_traces)
        _safe_data(preprocessed_data, threshold_total, threshold_occurrence_in_traces)
        preprocessed_data = _load_preprocessed_data(threshold_total, threshold_occurrence_in_traces)

    if preprocessed_data:
        return preprocessed_data, original_data
    else:
        print('No data available.')
        exit(0)
