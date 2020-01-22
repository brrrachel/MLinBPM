import datetime
from pytimeparse.timeparse import timeparse
from utils import get_activities, get_resources, get_earliest_trace, get_latest_trace, get_trace_endtime, proceed_resources, get_time_range
from resource import Resource
from simulator import Simulator


class QValueAllocator:
    q = {}
    lr = 0.5
    gamma = 0.9
    resources = {}
    results = {}

    def __init__(self):
        return

    def _get_available_resources(self):
        available_resources = []
        for resource_id in self.resources.keys():
            resource = self.resources[resource_id]
            if resource.workload < 1:
                available_resources.append(resource_id)
        return available_resources

    def fit(self, data):

        activities = get_activities(data)
        resources = get_resources(data)

        # init q_value dict
        for event in activities:
            self.q[event] = {}
            for resource in resources:
                self.q[event][resource] = 0

        # add resources
        for resource_id in resources:
            self.resources[resource_id] = Resource(self, resource_id, None)

        # iterate over each event of the traces and update the q-value dict by update formula
        for trace_number in data:
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
        # print qvalue table
        # for action in self.q:
        #     for resource in self.q[action]:
        #         print(action + ": " + resource + ": " + str(self.q[action][resource]))
        return self

    def allocate_resource(self, trace_id, activity):
        # if there are any:
        available_resources = self._get_available_resources()
        if available_resources:
            # find best resource regarding the qValue
            best_resource = self.resources[available_resources[0]]
            for resource_id in available_resources:
                resource = self.resources[resource_id]
                if self.q[activity['activity']][resource.resource_id] != 0:
                    if self.q[activity['activity']][resource.resource_id] > self.q[activity['activity']][best_resource.get_resource_id()]:
                        best_resource = resource
            print("Resource " + str(best_resource.resource_id) + " allocated for activity '" + activity['activity'] + "' of trace " + trace_id + " and has now a workload of " + str(best_resource.workload + 1) + ".")
            abs_q_value = self.q[activity['activity']][best_resource.resource_id]
            activity['duration'] = abs_q_value
            best_resource.allocate_for_activity(trace_id, activity)
            return 'busy', best_resource.resource_id
        else:
            return 'free', None

    def predict(self, data, interval):
        return Simulator(self).start(data, interval)
