import datetime
from pytimeparse.timeparse import timeparse
from utils import get_activities, get_resources, get_earliest_trace, get_latest_trace, get_trace_endtime, proceed_resources, get_time_range
from resource import Resource
from dateutil.parser import parse
from tqdm import tqdm


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
                available_resources.append(resource_id)
        return available_resources

    def allocate_activities(self, current_time, allocator):
        # All available traces which need to be allocated
        for trace_id in allocator.enabled_traces:
            trace_activities = allocator.enabled_traces[trace_id]
            if trace_activities:
                if trace_activities[0]['status'] == 'free':
                    trace_activities[0]['status'] = allocator.allocate_resource(trace_id, trace_activities[0])
                    if trace_activities[0]['status'] == 'busy':
                        trace_activities[0]['start'] = current_time
                elif trace_activities[0]['status'] == 'done':
                    # remove activity from trace
                    trace_activities[0]['end'] = current_time
                    # trace_activities[0]['duration'] = trace_activities[0]['end'] - trace_activities[0]['start']
                    allocator.results[trace_id].append(trace_activities[0])
                    trace_activities.pop(0)
                    if trace_activities:
                        trace_activities[0]['status'] = allocator.allocate_resource(trace_id, trace_activities[0])
                else:  # busy
                    continue
        return

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
                if self.q[activity['activity']][resource.get_resource_id()] != 0:
                    if self.q[activity['activity']][resource.get_resource_id()] > self.q[activity['activity']][
                        best_resource.get_resource_id()]: best_resource = resource
            # print("Resource " + str(best_resource.get_resource_id()) + " allocated for activity " + activity['activity'] + ".\n")
            abs_q_value = self.q[activity['activity']][best_resource.get_resource_id()]
            best_resource.allocate_for_activity(trace_id, activity, abs_q_value)
            return 'busy'
        else:
            return 'free'

    def proceed_resources(self):
        for resource_id in self.resources:
            resource = self.resources[resource_id]
            if not resource.is_available:
                finished = resource.proceed_activity()
                if finished:
                    trace_id = resource.trace_id
                    self.enabled_traces[trace_id][0]['status'] = 'done'
                    resource.reset()

    def predict(self, data):
        results = {}
        trace_ids = list(data.keys())
        start_time = parse(get_earliest_trace(data)['start'])
        time_range = get_time_range(data, start_time)

        for i in tqdm(range(0, time_range, 120)):
            # Search for new traces at actual time
            for j, trace_key in enumerate(trace_ids):
                trace = data[trace_key]
                results[trace_key] = []
                if (parse(trace['start']) - start_time).total_seconds() <= i:
                    self.enabled_traces[trace_key] = list(trace['events'])
                    # print('trace: ' + trace_key + ' is started.')
                    trace_ids.pop(j)

            # All available traces which need to be allocated
            for trace_id in self.enabled_traces:
                trace_activities = self.enabled_traces[trace_id]
                if trace_activities:
                    if trace_activities[0]['status'] == 'free':
                        trace_activities[0]['status'] = self.allocate_resource(trace_id, trace_activities[0])
                        if trace_activities[0]['status'] == 'busy':
                            trace_activities[0]['start'] = start_time + datetime.timedelta(seconds=i)
                    elif trace_activities[0]['status'] == 'done':
                        # remove activity from trace
                        trace_activities[0]['end'] = start_time + datetime.timedelta(seconds=i)
                        # trace_activities[0]['duration'] = trace_activities[0]['end'] - trace_activities[0]['start']
                        results[trace_id].append(trace_activities[0])
                        trace_activities.pop(0)
                        if trace_activities:
                            trace_activities[0]['status'] = self.allocate_resource(trace_id, trace_activities[0])
                    else:  # busy
                        continue
            self.proceed_resources()
            # self.resources, self.enabled_traces = proceed_resources(self.resources, self.enabled_traces)
            # if len(self.enabled_traces) == len(trace_ids):
            #     finished = True
            #     for trace_id in self.enabled_traces:
            #         trace = self.enabled_traces[trace_id]
            #         if trace:
            #             finished = False
            #     if finished:
            #         i = int((end_time_allocation - start_time).total_seconds())
        for trace in self.enabled_traces:
            print(trace, len(self.enabled_traces[trace]))
