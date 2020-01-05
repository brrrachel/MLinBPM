from utils import get_resources, get_activities_for_resource
from resource import Resource


class GreedyAllocator:

    resources = {}

    def __init__(self):
        return

    def fit(self, data):
        # create resources
        resources = get_resources(data)
        for id in resources:
            skills = get_activities_for_resource(data, id)
            self.resources[id] = Resource(id, skills)
        return self

    def predict(self, data):

        return
