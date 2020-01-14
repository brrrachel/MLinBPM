from dateutil.parser import parse
import datetime


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
    print("reguläres Ende des Logs: " + str(end))
    return latest_trace


def get_earliest_trace(data):
    earliest_trace = data[next(iter(data.keys()))]
    for trace_id in data.keys():
        trace = data[trace_id]
        if parse(trace['start']) > parse(earliest_trace['start']):
            earliest_trace = trace
    return earliest_trace


def get_activities_for_resource(data, resource_id):
    activities = set()
    for trace in data.keys():
        for event in data[trace]['events']:
            if event['resource'] == resource_id:
                activities.add(event['activity'])
    return activities


def get_resources(data):
    resources = []
    for trace in data.keys():
        resources += [event['resource'] for event in data[trace]['events']]
    return set(resources)


def get_time_range(data, start_time):
    latest_trace = get_latest_trace(data)
    print(get_trace_endtime(latest_trace))
    end_time_allocation = get_trace_endtime(latest_trace)
    return int((end_time_allocation - start_time).total_seconds())

def proceed_resources(self, resources, enabled_traces):
    for resource_id in resources:
        resource = resources[resource_id]
        if not resource.is_available:
            finished = resource.proceed_activity()
            if finished:
                trace_id = resource.trace_id
                enabled_traces[trace_id][0]['status'] = 'done'
                resource.reset()
    return resources, enabled_traces
