import datetime
from pytimeparse.timeparse import timeparse
import random


class Resource:
    resource_id = None
    is_available = True
    activity_id = {}
    activity = None
    trace_id = None
    allocator = None
    duration = None
    skills = None

    def __init__(self, allocator, resource_id, skills):
        self.resource_id = resource_id
        self.skills = skills
        self.allocator = allocator

    def get_resource_id(self):
        return str(self.resource_id)

    def reset(self):
        self.activity = None
        self.trace_id = None
        self.is_available = True

    def proceed_activity(self):
        percentage = random.uniform(0, 1)
        if percentage > 0.001:
            self.duration -= 1
        if self.duration == 0:
            print("Resource " + str(self.resource_id) + " finished activity " + self.activity['activity'] + ".")
            return True
        else:
            return False

    def allocate_for_activity(self, trace_id, activity, planned_time):
        self.is_available = False
        self.activity = activity
        self.trace_id = trace_id
        self.duration = max(int(planned_time / 30), 1)
