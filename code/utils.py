from dateutil.parser import parse
import datetime
import math


def _get_cases(data):
    cases = set()
    for trace in data.keys():
        cases.add(tuple([event['activity'] for event in data[trace]['events']]))
    return cases


def get_activities(data):
    activities = []
    for trace in data.keys():
        activities += [event['activity'] for event in data[trace]['events']]
    return set(activities)


def get_trace_endtime(trace):
    if type(trace['start']) is str:
        start = parse(trace['start'])
    else:
        start = trace['start']
    duration = datetime.timedelta(hours=0, minutes=0, seconds=0)
    for event in trace['events']:
        if type(event['duration']) is str:
            if ' days, ' in event['duration']:
                days, timestamp = event['duration'].split(' days, ')
            elif ' day, ' in event['duration']:
                days, timestamp = event['duration'].split(' day, ')
            else:
                timestamp = event['duration']
                days = 0
            t = datetime.datetime.strptime(timestamp, "%H:%M:%S") + datetime.timedelta(days=int(days))
            duration += datetime.timedelta(days=t.day, hours=t.hour, minutes=t.minute, seconds=t.second)
        else:
            duration += event['duration']
    return start + duration


def get_earliest_trace(data):
    earliest_trace = data[next(iter(data.keys()))]
    for trace_id in data.keys():
        trace = data[trace_id]
        if parse(trace['start']) < parse(earliest_trace['start']):
            earliest_trace = trace
    return earliest_trace


def get_latest_trace(data):
    latest_trace = data[next(iter(data.keys()))]
    if latest_trace['end'] != '':
        latest_end = parse(latest_trace['end'])
    else:
        latest_end = get_trace_endtime(latest_trace)
    for trace_id in data.keys():
        trace = data[trace_id]
        if trace['end'] != '':
            end = parse(trace['end'])
        else:
            end = get_trace_endtime(trace)
        if end > latest_end:
            latest_trace = trace
    print("regular end of the log: " + str(end))
    return latest_trace


def get_activities_for_resource(data, resource_id):
    activities = {}
    for trace in data.keys():
        for event in data[trace]['events']:
            if event['resource'] == resource_id:
                activity = event['activity']
                if activity in activities.keys():
                    # update duration
                    activities[activity] = (activities[activity] + parse_timedelta(event['duration']).total_seconds()) / 2
                else:
                    # create entry for this activity
                    activities[activity] = parse_timedelta(event['duration']).total_seconds()

    return activities


def get_resource_ids(data):
    resources = []
    for trace in data.keys():
        resources += [event['resource'] for event in data[trace]['events']]
    return set(resources)


def get_available_resources(resources, workload):
    available_resources_id = []
    for resource_id in resources.keys():
        resource = resources[resource_id]
        if resource.workload < workload:
            available_resources_id.append(resource_id)
    return available_resources_id


def get_time_range(data, start_time):
    latest_trace = get_latest_trace(data)
    end_time_allocation = get_trace_endtime(latest_trace)
    return int((end_time_allocation - start_time).total_seconds())


def proceed_resources(time, enabled_traces, resources):
    if 9 <= time.hour < 17:
        for resource_id in resources:
            resource = resources[resource_id]
            if resources[resource_id].workload > 0:
                finished = resource.proceed_activity(time)
                if finished:
                    enabled_traces[resource.trace_id][0]['status'] = 'done'
                    resource.set_as_free()
    return resources, enabled_traces


def compute_timedelta(seconds):
    num_days = math.floor(seconds / (24 * 3600))
    rest_seconds = seconds - (num_days * 24 * 3600)
    num_hours = math.floor(rest_seconds / 3600)
    rest_seconds = rest_seconds - (num_hours * 3600)
    num_minutes = math.floor(rest_seconds / 60)
    rest_seconds = rest_seconds - (num_minutes * 60)
    return datetime.timedelta(days=num_days, hours=num_hours, minutes=num_minutes, seconds=rest_seconds)


def parse_timedelta(text):
    days = None
    timestamp = None
    if ' days, ' in text:
        days, timestamp = text.split(' days, ')
    elif ' day, ' in text:
        days, timestamp = text.split(' day, ')
    else:
        days = 0
        timestamp = text
    t = datetime.datetime.strptime(timestamp, "%H:%M:%S") + datetime.timedelta(days=int(days))
    return datetime.timedelta(days=t.day, hours=t.hour, minutes=t.minute, seconds=t.second)