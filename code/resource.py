import datetime
from pytimeparse.timeparse import timeparse
import random


class Resource:
    resource_id = None
    is_available = True
    activity = None
    allocator = None
    duration = None
    skills = None

    def __init__(self, allocator, resource_id, skills):
        self.resource_id = resource_id
        self.skills = skills
        self.allocator = allocator

    def get_resource_id(self):
        return str(self.resource_id)

    def proceed_activity(self):
        percentage = random.uniform(0, 1)
        if percentage < 0.15:
            self.duration -= 1
        if self.duration == 0:
            self.is_available = True
            self.activity = None
            print("Resource " + str(self.resource_id) + " finished activity " + self.activity['activity'] + ".")
            return True
        else:
            return False

    def allocate_for_activity(self, activity):
        self.is_available = False
        self.activity = activity
        duration = timeparse(activity['duration'])
        duration_in_sec = datetime.timedelta(duration).total_seconds()
        self.duration = duration_in_sec
