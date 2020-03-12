from utils import compute_timedelta, get_activities, get_resource_ids, get_available_resources, parse_timedelta
from allocator.qValue import QValueAllocator
from resource import Resource
import math


class QValueAllocatorMultiDimension(QValueAllocator):

    def fit(self, data, salary):

        activities = get_activities(data)
        resources = get_resource_ids(data)

        # init q_value dict
        for event in activities:
            self.q[event] = {}
            for resource in resources:
                self.q[event][resource] = (0, 0)

        # add resources
        for resource_id in resources:
            self.resources[resource_id] = Resource(self, resource_id, None, salary[resource_id]['salary'])

        # iterate over all traces in log
        for trace_number in data:
            trace = data[trace_number]

            # iterate over each activity instance in trace
            for i in range(len(trace['events'])):
                event = trace['events'][i]
                activity = event['activity']
                resource = event['resource']
                duration = parse_timedelta(event['duration']).total_seconds()
                minute_wage = self.resources[resource].salary / 3600

                # when the first matching activity instance for an activity is found
                if self.q[activity][resource][0] == 0:
                    self.q[activity][resource] = (duration * (self.resources[resource].salary / 3600), duration)
                    continue

                # consider only activity instances which have a following activity instance
                if i < len(trace['events']) - 1:
                    new_activity = trace['events'][i + 1]['activity']

                    # find the minimal qValue of all resources
                    q_min = 10000000000000000000
                    for q_action in self.q[new_activity]:
                        if self.q[new_activity][q_action][0] < q_min:
                            q_min = self.q[new_activity][q_action][0]

                    # update q-Value in look up table
                    current_qvalue = self.q[activity][resource][1]
                    expected_duration = round(current_qvalue + self.lr * ((duration + (self.gamma * q_min)) - current_qvalue), 2)
                    self.q[activity][resource] = (expected_duration * minute_wage, expected_duration)
                else:
                    # if this is the last activity instance in trace
                    current_qvalue = self.q[activity][resource][1]
                    expected_duration = round(current_qvalue + self.lr * (duration - current_qvalue), 2)
                    self.q[activity][resource] = (expected_duration * minute_wage, expected_duration)

        return self

    def allocate_resource(self, trace_id, activity):
        available_resources = get_available_resources(self.resources, self.workload)
        if available_resources:

            # take the first fitting resource
            first_resource_key = None
            for resource_iter in self.q[activity['activity']]:
                if self.q[activity['activity']][resource_iter][0] > 0:
                    first_resource_key = resource_iter
                    break

            # find a better fitting resource
            best_resource = self.resources[first_resource_key]
            for resource_id in available_resources:
                resource = self.resources[resource_id]

                # only consider resources which have executed this activity ( qValue != 0 )
                if self.q[activity['activity']][resource.resource_id][0] != 0:

                    # if a resource with a better q-Value has been found
                    another_resource_qvalue = self.q[activity['activity']][resource_id]
                    best_resource_qvalue = self.q[activity['activity']][best_resource.resource_id]
                    if another_resource_qvalue < best_resource_qvalue:
                        best_resource = resource

            if self.q[activity['activity']][best_resource.resource_id][0] == 0:
                # no fitting resource found
                return 'free', None

            else:
                # fitting resource found and assign activity instance
                expected_duration = compute_timedelta(math.ceil(self.q[activity['activity']][best_resource.resource_id][1]))
                activity['duration'] = expected_duration
                best_resource.allocate_for_activity(trace_id, activity)
                return 'busy', best_resource.resource_id
        else:
            # at the moment all resources are busy
            return 'free', None
