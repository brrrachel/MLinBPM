import numpy as np
from collections import Counter


def get_occurence(data):
    events = []
    resources = []
    for trace in data.keys():
        events += [event['activity'] for event in data[trace]['events']]
        resources += [event['resource'] for event in data[trace]['events']]
    return set(events), set(resources)


class QValueAllocator():

    q = {}
    lr = 0.5
    gamma = 0.9

    def __init__(self):
        return

    def fit(self, data):
        # init q_value dict
        events, resources = get_occurence(data)
        for event in events:
            self.q[event] = {}
            for resource in resources:
                self.q[event][resource] = 0

        # iterate over each event of the traces and update the q-value dict by update formula
        for tracenumber in data:
            trace = data[tracenumber]
            print(trace)
            for i in range(len(trace['events'])):
                event = trace.events[i]
                state = event['activity']
                action = event['resource']
                if i < len(trace.events) - 1:
                    new_state = trace.events[i+1]['activity']
                    q_min = 1000000000000000
                    for q_action in self.q[new_state]:
                        if self.q[new_state][q_action] < q_min:
                            q_min = self.q[new_state][q_action]
                    self.q[state][action] = (self.lr - 1) * self.q[state][action] + self.lr * (event['duration'] + (self.gamma * q_min))
        for action in self.q:
            print(action)
        return self

    def predict(self, X):
        return []

