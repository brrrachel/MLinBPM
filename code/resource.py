import random


class Resource:

    resource_id = None
    workload = 0
    activity_id = {}
    activity = None
    trace_id = None
    allocator = None
    planned_duration = None
    actual_duration = 0
    skills = None
    queue = []

    def __init__(self, allocator, resource_id, skills):
        self.resource_id = resource_id
        self.skills = skills
        self.allocator = allocator

    def get_resource_id(self):
        return str(self.resource_id)

    def set_as_free(self):
        self.activity = None
        self.trace_id = None
        self.planned_duration = 0
        self.actual_duration = 0

    def proceed_activity(self, time):
        if self.activity is None:
            self.activity = self.queue[0][0]
            self.trace_id = self.queue[0][1]
            self.planned_duration = max(int(self.activity['duration'] / 7200), 1)
            self.queue.pop(0)
        percentage = random.uniform(0, 1)
        if 0.0001 > percentage < 0.0009:
            self.planned_duration -= 1
        elif percentage > 0.0009:
            self.planned_duration -= 2
        self.actual_duration += 1
        if self.planned_duration <= 0:
            self.workload -= 1
            print(time.__str__() + " : Resource " + str(self.resource_id) + " finished activity '" + self.activity['activity'] + "' and has a workload of " + str(self.workload) + " now.")
            return True
        else:
            return False

    def allocate_for_activity(self, trace_id, activity):
        self.workload += 1
        self.queue.append((activity, trace_id))
