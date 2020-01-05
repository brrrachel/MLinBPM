import datetime
import time
import threading
from pytimeparse.timeparse import timeparse
from utils import get_activities, get_resources
from resource import Resource


class QValueAllocator:
    q = {}
    lr = 0.5
    gamma = 0.9
    resources = {}

    def __init__(self):
        return

    def _get_available_resources(self):
        available_resources = []
        for resource in self.resources:
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
        for id in resources:
            self.resources[id] = Resource(id)

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

    def predict(self, activities):
        i = 0
        # iterate over all activities
        while i < len(activities):
            activity = activities[i]
            # get available resources
            available_resources = self._get_available_resources()
            # if there are any:
            if available_resources:
                # find best resource regarding the qValue
                best_resource = available_resources[0]
                for resource in available_resources:
                    if self.q[activity['activity']][resource.resource_id] < self.q[activity['activity']][best_resource.resource_id]:
                        best_resource = resource
                # create thread for executing activity
                executing_activity = threading.Thread(target=best_resource.allocate_for_activity(activity))
                # run thread
                executing_activity.start()
                print("Resource {} is executing activity {} .").format(best_resource.resource_id, activity['activity'])
                # go to next activity
                i += 1
            else:
                # no resource is available therefore sleep one second and try again
                print("no resources available --> waiting for resource ...")
                time.sleep(1)
        print("finished assigning tasks")
