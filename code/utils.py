from dateutil.parser import parse


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


def get_latest_trace(data):
    latest_trace = data[next(iter(data.keys()))]
    for trace_id in data.keys():
        trace = data[trace_id]
        if parse(trace['end']) > parse(latest_trace['end']):
            latest_trace = trace
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
