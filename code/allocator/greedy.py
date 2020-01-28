import random
from utils import get_resource_ids, get_available_resources, get_activities_for_resource
from resource import Resource


class GreedyAllocator:

    resources = {}

    def __init__(self):
        return

    def fit(self, data):
        resources_ids = get_resource_ids(data)
        for id in resources_ids:
            skills = get_activities_for_resource(data, id)
            self.resources[id] = Resource(self, id, skills, None)
        return self

    def allocate_resource(self, trace_id, activity):
        available_resources = get_available_resources(self.resources, 1)
        if available_resources:

            random_resource_id = random.choice(available_resources)
            resource = self.resources[random_resource_id]
            while activity['activity'] not in resource.skills.keys():
                available_resources.remove(random_resource_id)
                if len(available_resources) > 0:
                    random_resource_id = random.choice(available_resources)
                    resource = self.resources[random_resource_id]
                else:  # if no resource with the needed skill has been found
                    return 'free', None

            print("Resource " + str(random_resource_id) + " allocated for activity '" + activity['activity'] + "' of trace " + trace_id + " and has now a workload of " + str(resource.workload + 1) + ".")
            activity['duration'] = resource.skills[activity['activity']]
            resource.allocate_for_activity(trace_id, activity)
            return 'busy', random_resource_id
        else:
            return 'free', None
