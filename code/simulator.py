from tqdm import tqdm
from dateutil.parser import parse
from utils import get_activities, get_resources, get_earliest_trace, get_latest_trace, get_trace_endtime, proceed_resources, get_time_range, compute_timedelta


class Simulator:

    allocator = None
    trace_ids = None
    enabled_traces = {}
    results = {}

    def __init__(self, allocator):
        self.allocator = allocator
        return

    def _search_for_new_traces(self, data, current_time):
        for j, trace_key in enumerate(self.trace_ids):
            if parse(data[trace_key]['start']) <= current_time:
                self.results[trace_key] = []
                self.enabled_traces[trace_key] = list(data[trace_key]['events'])
                self.trace_ids.pop(j)

    def _remove_activity_from_trace(self, trace_id, current_time):
        self.enabled_traces[trace_id][0]['end'] = current_time
        self.enabled_traces[trace_id][0]['duration'] = current_time - self.enabled_traces[trace_id][0]['start']
        self.results[trace_id].append(self.enabled_traces[trace_id][0])
        self.enabled_traces[trace_id].pop(0)
        if len(self.enabled_traces[trace_id]) == 0:
            self.enabled_traces.pop(trace_id)

    def _allocate_activity(self, trace_id, current_time):
        new_status, resource = self.allocator.allocate_resource(trace_id, self.enabled_traces[trace_id][0])
        self.enabled_traces[trace_id][0]['status'] = new_status
        self.enabled_traces[trace_id][0]['resource'] = resource
        if self.enabled_traces[trace_id][0]['status'] == 'busy':
            self.enabled_traces[trace_id][0]['start'] = current_time
            activity_start = self.enabled_traces[trace_id][0]['start'].__str__()
            print('Trace ' + trace_id + ': Activity started at ' + activity_start + '.')

    def start(self, data, interval):
        self.trace_ids = list(data.keys())
        start_time = parse(get_earliest_trace(data)['start'])
        sim_interval = compute_timedelta(interval)
        print('start time', start_time)
        print('simulation interval', sim_interval)
        # time_range = get_time_range(data, start_time)

        # for i in tqdm(range(0, time_range, interval)):
        #     current_time = start_time + compute_timedelta(i)
        #
        #     self._search_for_new_traces(data, current_time)
        #
        #     # All available traces which need to be allocated
        #     for trace_id in list(self.enabled_traces.keys()):
        #         if self.enabled_traces[trace_id][0]['status'] == 'done':
        #             self._remove_activity_from_trace(trace_id, current_time)  # removes also trace from enabled_traces if all activities are done
        #         if trace_id in self.enabled_traces:
        #             if self.enabled_traces[trace_id][0]['status'] == 'free':
        #                 self._allocate_activity(trace_id, current_time)
        #
        #     self.allocator.resources, self.enabled_traces = proceed_resources(self.enabled_traces, self.allocator.resources)

        # when all remaining traces are allocated and only need to be finished for finishing the simulation
        current_time = start_time
        # total_num_trace_ids = len(self.trace_ids)
        while len(self.enabled_traces) > 0 or len(self.trace_ids) > 0:
            self._search_for_new_traces(data, current_time)
            if list(self.enabled_traces.keys()):
                for trace_id in list(self.enabled_traces.keys()):
                    if self.enabled_traces[trace_id][0]['status'] == 'done':
                        self._remove_activity_from_trace(trace_id, current_time)  # removes also trace from enabled_traces if all activities are done
                    if trace_id in self.enabled_traces:
                        if self.enabled_traces[trace_id][0]['status'] == 'free':
                            self._allocate_activity(trace_id, current_time)
                    self.allocator.resources, self.enabled_traces = proceed_resources(self.enabled_traces, self.allocator.resources)

            # current_time += sim_interval
            # finished_traces = total_num_trace_ids - len(self.trace_ids)
            # frac = finished_traces/total_num_trace_ids
            # print('\r[{:>7.2%}]'.format(frac))

        return self.results
