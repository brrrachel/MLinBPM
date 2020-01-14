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
    planned_duration = None
    actual_duration = 0
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
        self.planned_duration = 0
        self.actual_duration = 0

    def proceed_activity(self):
        percentage = random.uniform(0, 1)
        if 0.0001 < percentage < 0.0009:
            self.planned_duration -= 1
        elif percentage > 0.009:
            self.planned_duration -= 2
        self.actual_duration += 1
        if self.planned_duration <= 0:
            print("Resource " + str(self.resource_id) + " finished activity " + self.activity['activity'] + ".")
            return True
        else:
            return False

    def allocate_for_activity(self, trace_id, activity, planned_time):
        self.is_available = False
        self.activity = activity
        self.trace_id = trace_id
        self.planned_duration = max(int(planned_time / 120), 1)
