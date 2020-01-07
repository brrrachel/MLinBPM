import datetime
import time
from pytimeparse.timeparse import timeparse
from utils import get_activities, get_resources, get_earliest_trace, get_latest_trace
from resource import Resource
from dateutil.parser import parse


class QValueAllocator:
    q = {}
    lr = 0.5
    gamma = 0.9
    resources = {}
    enabled_traces = {}  # dictionary key: trace_id value: list of activities

    def __init__(self):
        return

    def _get_available_resources(self):
        available_resources = []
        for resource_id in self.resources.keys():
            resource = self.resources[resource_id]
            if resource.is_available:
                available_resources.append(resource)
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
                    reward = datetime.timedelta(duration).total_seconds()

                    q_min = 1000000000000000
                    for q_action in self.q[new_state]:
                        if self.q[new_state][q_action] < q_min:
                            q_min = self.q[new_state][q_action]
                    self.q[state][action] = (self.lr - 1) * self.q[state][action] + self.lr * (
                            reward + (self.gamma * q_min))
        for action in self.q:
            for resource in self.q[action]:
                print(action + ": " + resource + ": " + str(self.q[action][resource]))
        return self

    def allocate_resource(self, activity):
        # if there are any:
        available_resources = self._get_available_resources()
        if available_resources:
            # find best resource regarding the qValue
            best_resource = available_resources[0]
            for resource in available_resources:
                if self.q[activity['activity']][resource.get_resource_id()] != 0:
                    if self.q[activity['activity']][resource.get_resource_id()] < self.q[activity['activity']][
                        best_resource.get_resource_id()]:
                        best_resource = resource
            print("Resource " + str(best_resource.get_resource_id()) + " allocated for activity " + activity[
                'activity'] + ".")
            best_resource.allocate_for_activity(self, activity)
            return True
        else:
            print("no resources available --> waiting for resources ...")
            return False

    def proceed_resources(self):
        for resource in self.resources:
            if not resource.is_available:
                finished = resource.proceed_activity()

    def predict(self, data):
        earliest_trace = get_earliest_trace(data)
        latest_trace = get_latest_trace(data)
        actual_time = parse(earliest_trace['start'])
        trace_ids = list(data.keys())
        while actual_time <= parse(latest_trace['end']):

            # Search for new traces at actual time
            for i, trace_key in enumerate(trace_ids):
                trace = data[trace_key]
                if parse(trace['start']) == actual_time:
                    self.enabled_traces[trace_key] = list(trace['events'])
                    trace_ids.pop(i)

            # All available traces which need to be allocated
            for trace_id in self.enabled_traces:
                trace_activities = self.enabled_traces[trace_id]
                if trace_activities[0]['status'] == 'free':
                    trace_activities[0]['status'] = self.allocate_resource(trace_activities[0])
                elif trace_activities[0]['status'] == 'done':
                    # remove activity from trace
                    trace_activities.pop(0)
                    if trace_activities:
                        trace_activities[0]['status'] = self.allocate_resource(trace_activities[0])
                    else:
                        del (self.enabled_traces[trace_id])
                else:  # busy
                    break
            self.proceed_resources()
            actual_time += datetime.timedelta(seconds=1)
