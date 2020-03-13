from utils import get_activities, get_resource_ids, get_available_resources, parse_timedelta, compute_timedelta
from resource import Resource
from tqdm import tqdm
import math


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

        # iterate over all traces in log
        for trace_id in tqdm(data):
            trace = data[trace_id]

            # iterate over each activity instance in trace
            for i in range(len(trace['events'])):
                activity_instance = trace['events'][i]
                state = activity_instance['activity']
                activity = activity_instance['resource']
                duration = parse_timedelta(activity_instance['duration']).total_seconds()

                # when the first matching activity instance for an activity is found
                if self.q[state][activity] == 0:
                    # update value without the q-value formula
                    self.q[state][activity] = duration
                    continue

                # consider only activity instances which have a following activity instance
                if i < (len(trace['events']) - 1):
                    new_state = trace['events'][i + 1]['activity']
                    q_min = 1000000000000000

                    # find the minimal q-Value of all resources
                    for q_action in self.q[new_state]:
                        if self.q[new_state][q_action] < q_min:
                            q_min = self.q[new_state][q_action]

                    # update q-Value in look up table
                    current_qvalue = self.q[state][activity]
                    q_value = current_qvalue + self.lr * ((duration + (self.gamma * q_min)) - current_qvalue)
                    self.q[state][activity] = q_value
                else:
                    # if this is the last activity instance in trace
                    q_value = self.q[state][activity] + self.lr * (duration - self.q[state][activity])
                    self.q[state][activity] = q_value

        return self

    def allocate_resource(self, trace_id, activity):
        available_resources = get_available_resources(self.resources, self.workload)
        if available_resources:

            # take the first fitting resource
            first_resource_key = None
            for resource_iter in available_resources:
                if self.q[activity['activity']][resource_iter] > 0:
                    first_resource_key = resource_iter
                    break

            # find a better fitting resource
            best_resource = self.resources[first_resource_key]
            for resource_id in available_resources:
                resource = self.resources[resource_id]

                # only consider resources which have executed this activity ( qValue != 0 )
                if self.q[activity['activity']][resource_id] != 0:

                    # if a resource with a better q-Value has been found
                    another_resource_qvalue = self.q[activity['activity']][resource_id]
                    best_resource_qvalue = self.q[activity['activity']][best_resource.resource_id]
                    if another_resource_qvalue < best_resource_qvalue:
                        best_resource = resource

            if self.q[activity['activity']][best_resource.resource_id] == 0:
                # no fitting resource found
                return 'free', None
            else:
                # fitting resource found and assign activity instance
                expected_duration = compute_timedelta(
                    math.ceil(self.q[activity['activity']][best_resource.resource_id]))
                activity['duration'] = expected_duration
                best_resource.allocate_for_activity(trace_id, activity)
                return 'busy', best_resource.resource_id
        else:
            # at the moment all resources are busy
            return 'free', None
