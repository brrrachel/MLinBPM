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


def get_activities_for_resource(data, id):
    activities = set()
    for trace in data.keys():
        for event in data[trace]['events']:
            if event['resource'] == id:
                activities.add(event['activity'])
    return activities


def get_resources(data):
    resources = []
    for trace in data.keys():
        resources += [event['resource'] for event in data[trace]['events']]
    return set(resources)
