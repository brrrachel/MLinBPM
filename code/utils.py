import datetime
import math
from dateutil.parser import parse


def get_activities(data):
    # returns a sorted list of all activities
    activities = []
    for trace in data.keys():
        activities += [event['activity'] for event in data[trace]['events']]
    sorted_activities = list(sorted(set(activities)))
    return sorted_activities


def get_activities_for_resource(data, resource_id):
    # returns for a resource a set of all executed activities and the average execution time
    activities = {}
    for trace in data.keys():
        for event in data[trace]['events']:
            if event['resource'] == resource_id:
                activity = event['activity']
                if activity in activities.keys():
                    # update duration
                    activities[activity].append(parse_timedelta(event['duration']))
                else:
                    # create entry for this activity
                    activities[activity] = [parse_timedelta(event['duration'])]

    # calculates the average execution time for each activity
    for activity in activities.keys():
        activities[activity] = sum(activities[activity], datetime.timedelta()) / len(activities[activity])
    return activities


def get_resource_ids(data):
    # returns a set of all resource ids of the dataset
    resources = []
    for trace in data.keys():
        resources += [event['resource'] for event in data[trace]['events']]

    sorted_resources = list(sorted(set(resources)))
    return sorted_resources


def get_earliest_trace(data):
    # returns the trace of the log which starts at first
    earliest_trace = data[next(iter(data.keys()))]
    for trace_id in data.keys():
        trace = data[trace_id]
        if parse(trace['start']) < parse(earliest_trace['start']):
            earliest_trace = trace
    return earliest_trace


def normalize_salary(max_value):
    # returns two lists with the normalized salaries for the number of performed activities
    steps = range(0, max_value+1, 1)

    def normalize(x, m):
        return ((x ** 2) / m) + 10

    salary = [normalize(x, max_value) for x in steps]
    return steps, salary


def calculate_salaries(data):
    resources = get_resource_ids(data)
    result = {}

    # gets the number of performed activites for each resouce
    for resource_id in resources:
        result[resource_id] = {}
        result[resource_id]['activities'] = len(list(get_activities_for_resource(data, resource_id).keys()))

    # normalize the salary
    max_value = max([result[key]['activities'] for key in result.keys()])
    _, salary = normalize_salary(max_value)

    # assign each resource a salary
    for resource_id in resources:
        result[resource_id]['salary'] = salary[result[resource_id]['activities']]

    return result


def get_available_resources(resources, workload):
    # returns a list with available resources
    available_resources_id = []
    for resource_id in resources.keys():
        # a resource is available if the is still capacity left in its queue
        if resources[resource_id].workload < workload:
            available_resources_id.append(resource_id)
    return available_resources_id


def get_num_of_busy_resources(resources):
    # returns the number of resources which are currently working
    available_resources_id = []
    for resource_id in resources.keys():
        resource = resources[resource_id]
        if resource.workload > 0:
            available_resources_id.append(resource_id)
    return len(available_resources_id)


def compute_timedelta(seconds):
    # creates on a basis of a number of seconds a timedelta object
    num_days = math.floor(seconds / (24 * 3600))
    rest_seconds = seconds - (num_days * 24 * 3600)
    num_hours = math.floor(rest_seconds / 3600)
    rest_seconds = rest_seconds - (num_hours * 3600)
    num_minutes = math.floor(rest_seconds / 60)
    rest_seconds = rest_seconds - (num_minutes * 60)
    return datetime.timedelta(days=num_days, hours=num_hours, minutes=num_minutes, seconds=rest_seconds)


def parse_timedelta(text):
    # parses a string to a timedelta object
    days = None
    timestamp = None
    if ' days, ' in text:
        days, timestamp = text.split(' days, ')
    elif ' day, ' in text:
        days, timestamp = text.split(' day, ')
    else:
        days = 0
        timestamp = text
    t = datetime.datetime.strptime(timestamp, "%H:%M:%S")
    return datetime.timedelta(days=int(days), hours=t.hour, minutes=t.minute, seconds=t.second)
