import random


class Resource:

    resource_id = None
    workload = 0
    trace_id = None
    activity = None
    allocator = None
    planned_duration = None
    skills = None
    queue = []
    salary = None  # hourly wages

    def __init__(self, allocator, resource_id, skills, salary):
        self.resource_id = resource_id
        self.skills = skills
        self.allocator = allocator
        self.salary = salary

    def set_as_free(self):
        self.activity = None
        self.planned_duration = 0

    def proceed_activity(self, time):

        def _finish_activity():
            self.workload -= 1
            print(time.__str__() + " : Resource " + str(self.resource_id) + " finished activity '" + self.activity['activity'] + "' and has a workload of " + str(self.workload) + " now.")

        if self.activity is None:
            first_queue = self.queue.pop(0)
            self.trace_id = first_queue[0]
            self.activity = first_queue[1]
            self.planned_duration = self.activity['duration']


        if self.activity['start'] + self.planned_duration <= time:
            #print(self.resource_id, self.activity['start'], self.planned_duration)
            _finish_activity()
            return True
        else:
            percentage = random.uniform(0, 1)
            if percentage < 0.0001:
                print("random finish")
                _finish_activity()
                return True
            return False

    def allocate_for_activity(self, trace_id, activity):
        self.workload += 1
        self.queue.append((trace_id, activity))
