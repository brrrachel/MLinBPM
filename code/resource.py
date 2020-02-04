import random
import datetime
from dateutil.parser import parse


class Resource:

    resource_id = None
    workload = 0
    activity = None
    allocator = None
    planned_duration = None
    skills = None
    queue = []
    salary = None

    def __init__(self, allocator, resource_id, skills, salary):
        self.resource_id = resource_id
        self.skills = skills
        self.allocator = allocator
        self.salary = salary

    def get_resource_id(self):
        return str(self.resource_id)

    def set_as_free(self):
        self.activity = None
        self.trace_id = None
        self.planned_duration = 0

    def proceed_activity(self, time):

        def _finish_activity():
            self.workload -= 1
            print(time.__str__() + " : Resource " + str(self.resource_id) + " finished activity '" + self.activity['activity'] + "' and has a workload of " + str(self.workload) + " now.")
            return True

        if self.activity is None:
            self.activity = self.queue.pop(0)
            self.planned_duration = self.activity['duration']

        if self.activity['start'] + self.planned_duration <= time:
            _finish_activity()
        else:
            percentage = random.uniform(0, 1)
            if percentage < 0.001:
                _finish_activity()
            return False

    def allocate_for_activity(self, activity):
        self.workload += 1
        self.queue.append(activity)
