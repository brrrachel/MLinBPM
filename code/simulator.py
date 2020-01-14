from tqdm import tqdm
from dateutil.parser import parse
import datetime
from pytimeparse.timeparse import timeparse
from utils import get_activities, get_resources, get_earliest_trace, get_latest_trace, get_trace_endtime, proceed_resources, get_time_range

class Simulator:

    enabled_traces = {}
    results = {}

    def __init__(self):
        return

    def start(self, allocator, data):
        trace_ids = list(data.keys())
        start_time = parse(get_earliest_trace(data)['start'])
        time_range = get_time_range(data, start_time)

        for i in tqdm(range(0, time_range, 120)):
            # Search for new traces at actual time
            for j, trace_key in enumerate(trace_ids):
                trace = data[trace_key]
                self.results[trace_key] = []
                if (parse(trace['start']) - start_time).total_seconds() <= i:
                    self.enabled_traces[trace_key] = list(trace['events'])
                    print('trace: ' + trace_key + ' is started.')
                    trace_ids.pop(j)
            # All available traces which need to be allocated
            for trace_id in self.enabled_traces:
                trace_activities = self.enabled_traces[trace_id]
                if trace_activities:
                    if trace_activities[0]['status'] == 'free':
                        trace_activities[0]['status'] = allocator.allocate_resource(trace_id, trace_activities[0])
                        if trace_activities[0]['status'] == 'busy':
                            trace_activities[0]['start'] = start_time + datetime.timedelta(seconds=i)
                    elif trace_activities[0]['status'] == 'done':
                        # remove activity from trace
                        trace_activities[0]['end'] = start_time + datetime.timedelta(seconds=i)
                        # trace_activities[0]['duration'] = trace_activities[0]['end'] - trace_activities[0]['start']
                        if trace_id not in self.results.keys():
                            self.result[trace_id] = []
                        self.results[trace_id].append(trace_activities[0])

                        trace_activities.pop(0)
                        if trace_activities:
                            trace_activities[0]['status'] = allocator.allocate_resource(trace_id, trace_activities[0])
                    else:  # busy
                        continue

            allocator.resources, self.enabled_traces = proceed_resources(self.enabled_traces, allocator.resources)

        for trace in self.enabled_traces:
            print(trace, len(self.enabled_traces[trace]))

        return self.results
