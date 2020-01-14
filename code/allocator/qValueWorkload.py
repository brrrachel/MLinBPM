from allocator.qValue import QValueAllocator


class QValueAllocatorWorkload(QValueAllocator):

    def _get_available_resources(self):
        available_resources = []
        for resource_id in self.resources.keys():
            resource = self.resources[resource_id]
            if resource.workload < 3:
                available_resources.append(resource_id)
        return available_resources
