from allocator.qValue import QValueAllocator


class QValueAllocatorWorkload(QValueAllocator):

    workload = None

    def __init__(self, workload):
        self.workload = workload
        return

    def _get_available_resources(self):
        available_resources = []
        for resource_id in self.resources.keys():
            resource = self.resources[resource_id]
            if resource.workload < self.workload:
                available_resources.append(resource_id)
        return available_resources
