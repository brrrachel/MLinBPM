from pytimeparse.timeparse import timeparse
from utils import get_activities, get_resource_ids, get_available_resources, get_earliest_trace, get_latest_trace, get_trace_endtime, get_time_range, compute_timedelta
from resource import Resource
from tqdm import tqdm
import math
from plotting import resource_distribution


class QValueAllocator:

    q = {}
    lr = 0.5
    gamma = 0.9

    workload = 1
    resources = {}

    def __init__(self, workload):
        self.workload = workload
        return

    def fit(self, data, salary):

        activities = get_activities(data)
        resources = get_resource_ids(data)

        # init q_value dict
        for event in activities:
            self.q[event] = {}
            for resource in resources:
                self.q[event][resource] = 0

        # add resources
        for resource_id in resources:
            self.resources[resource_id] = Resource(self, resource_id, None, salary[resource_id]['salary'])

        # iterate over each event of the traces and update the q-value dict by update formula
        for trace_number in tqdm(data):
            trace = data[trace_number]
            for i in range(len(trace['events'])):
                event = trace['events'][i]
                state = event['activity']
                action = event['resource']
                if i < len(trace['events']) - 1:
                    new_state = trace['events'][i + 1]['activity']
                    duration = timeparse(event['duration'])

                    q_min = 1000000000000000
                    for q_action in self.q[new_state]:
                        if self.q[new_state][q_action] < q_min:
                            q_min = self.q[new_state][q_action]
                    self.q[state][action] = abs(round((self.lr - 1) * self.q[state][action] + self.lr * (
                            duration + (self.gamma * q_min)), 2))

        resource_distribution(self.q)
        return self

    def allocate_resource(self, trace_id, activity):
        available_resources = get_available_resources(self.resources, self.workload)
        if available_resources:
            # find best resource regarding the qValue
            first_resource_key = None
            for resource_iter in self.q[activity['activity']]:
                if self.q[activity['activity']][resource_iter] > 0:
                    first_resource_key = resource_iter
                    break
            best_resource = self.resources[first_resource_key]
            for resource_id in available_resources:
                resource = self.resources[resource_id]
                if self.q[activity['activity']][resource_id] != 0:
                    if self.q[activity['activity']][resource_id] < self.q[activity['activity']][best_resource.resource_id]:
                        best_resource = resource

            if self.q[activity['activity']][best_resource.resource_id] == 0:
                return 'free', None
            else:
                expected_duration = compute_timedelta(math.ceil(self.q[activity['activity']][best_resource.resource_id]))
                activity['duration'] = expected_duration
                best_resource.allocate_for_activity(trace_id, activity)
                return 'busy', best_resource.resource_id
        else:

            return 'free', None
