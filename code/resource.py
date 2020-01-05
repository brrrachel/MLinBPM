import datetime
import time
from pytimeparse.timeparse import timeparse


class Resource:
    resource_id = None
    is_available = True
    activity = None
    skills = None

    def __init__(self, resource_id, skills):
        self.resource_id = resource_id
        self.skills = skills

    def simulate_busy(self, sec):
        for i in range(0, sec):
            time.sleep(0.01)
        self.is_available = True
        print("Resource {} finished activity {} .").format(self.resource_id, self.activity['activity'])
        self.activity = None

    def allocate_for_activity(self, activity):
        self.is_available = False
        self.activity = activity
        duration = timeparse(activity['duration'])
        duration_in_sec = datetime.timedelta(duration).total_seconds()
        self.simulate_busy(duration_in_sec)
