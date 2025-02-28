import random
from utils import get_resource_ids, get_available_resources, get_activities_for_resource
from resource import Resource


class GreedyAllocator:

    resources = {}
    workload = 1

    def __init__(self, workload):
        self.workload = workload
        return

    def fit(self, data, salary):
        resources_ids = get_resource_ids(data)

        # collect for each resource its executed activities and create a resource object
        for id in resources_ids:
            skills = get_activities_for_resource(data, id)
            self.resources[id] = Resource(self, id, skills, salary[id]['salary'])

        return self

    def allocate_resource(self, trace_id, activity):

        available_resources = get_available_resources(self.resources, self.workload)
        if available_resources:

            # pick a random resource
            random_resource_id = random.choice(available_resources)
            resource = self.resources[random_resource_id]

            # if resource does not provide the required skill search for another capable resource
            while activity['activity'] not in resource.skills.keys():
                available_resources.remove(random_resource_id)
                if len(available_resources) > 0:
                    random_resource_id = random.choice(available_resources)
                    resource = self.resources[random_resource_id]
                else:  # if no resource with the needed skill has been found
                    return 'free', None

            # set the expected duration and as busy
            activity['duration'] = resource.skills[activity['activity']]
            resource.allocate_for_activity(trace_id, activity)
            return 'busy', random_resource_id

        else:
            # all resources are currently busy
            return 'free', None
