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
        # is called if an resource has been finished with the execution of an acitivity instance
        self.activity = None
        self.planned_duration = 0

    def allocate_for_activity(self, trace_id, activity_instance):
        # is called when a resource has been assigned to an activity instance
        self.workload += 1
        self.queue.append((trace_id, activity_instance))

    def proceed_activity(self, time):

        if self.activity is None:
            # if a resource has been finished with an activity instance and takes the next activity instance from queue
            first_queue = self.queue.pop(0)
            self.trace_id = first_queue[0]
            self.activity = first_queue[1]
            self.planned_duration = self.activity['duration']

        if (self.activity['start'] + self.planned_duration) <= time:
            # completed activity instance
            self.workload -= 1
            print(time.__str__() + " : Resource " + str(self.resource_id) + " finished activity '" + self.activity['activity'] + "' and has a workload of " + str(self.workload) + " now.")
            return True
        else:
            # if the resource is still working on the activity instance
            return False
