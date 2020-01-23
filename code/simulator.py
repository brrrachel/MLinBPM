import progressbar
import datetime
from dateutil.parser import parse
from utils import get_earliest_trace, proceed_resources, compute_timedelta


class Simulator:

    allocator = None
    trace_ids = None
    enabled_traces = {}
    results = {}

    end = None
    current_time = None
    interval = None
    bar = None
    progressbar_widgets = None
    finished = 0

    def __init__(self, interval, end):
        self.interval = compute_timedelta(interval)
        print('Simulation interval: ', self.interval)
        self.end = datetime.datetime.strptime(end, "%Y/%m/%d").__str__()

    def _search_for_new_traces(self, data, current_time):
        for j, trace_key in enumerate(self.trace_ids):
            if parse(data[trace_key]['start']) <= current_time:
                self.results[trace_key] = []
                self.enabled_traces[trace_key] = list(data[trace_key]['events'])
                self.trace_ids.pop(j)

    def _remove_activity_from_trace(self, trace_id):
        self.enabled_traces[trace_id][0]['end'] = self.current_time
        self.enabled_traces[trace_id][0]['duration'] = self.current_time - self.enabled_traces[trace_id][0]['start']
        self.results[trace_id].append(self.enabled_traces[trace_id][0])
        self.enabled_traces[trace_id].pop(0)
        if len(self.enabled_traces[trace_id]) == 0:
            self.enabled_traces.pop(trace_id)

    def _allocate_activity(self, trace_id):
        new_status, resource_id = self.allocator.allocate_resource(trace_id, self.enabled_traces[trace_id][0])
        self.enabled_traces[trace_id][0]['status'] = new_status
        self.enabled_traces[trace_id][0]['resource'] = resource_id
        if self.enabled_traces[trace_id][0]['status'] == 'busy':
            self.enabled_traces[trace_id][0]['start'] = self.current_time
            activity = self.enabled_traces[trace_id][0]['activity']
            workload = str(self.allocator.resources[resource_id].workload)
        print(self.current_time.__str__(), ": Resource " + resource_id + " allocated for activity '" + activity + "' of trace " + trace_id + " and has now a workload of " + workload + ".")

    def _update_progress_bar(self):
        self.progressbar_widgets[1] = self.current_time.__str__()
        amount_of_finished = 0
        for trace_key in self.results.keys():
            if not trace_key in self.enabled_traces:
                amount_of_finished += 1
        self.bar.update(amount_of_finished)
        self.current_time += self.interval

    def start(self, allocator, data):
        self.allocator = allocator
        self.trace_ids = list(data.keys())
        self.current_time = parse(get_earliest_trace(data)['start'])
        self.progressbar_widgets = [
            ' (Simulation Time: ', self.current_time.__str__(), '/', self.end, ') ',
            progressbar.Bar(marker='#'), progressbar.SimpleProgress(),
            ' Finished Traces (', progressbar.Timer(), ') ',
        ]

        print('--------------------------------------------------------------------------')
        self.bar = progressbar.ProgressBar(maxval=len(self.trace_ids), redirect_stdout=True, widgets=self.progressbar_widgets)
        self.bar.start()
        while len(self.enabled_traces) > 0 or len(self.trace_ids) > 0:
            self._search_for_new_traces(data, self.current_time)
            if list(self.enabled_traces.keys()):
                for trace_id in list(self.enabled_traces.keys()):
                    if self.enabled_traces[trace_id][0]['status'] == 'done':
                        self._remove_activity_from_trace(trace_id)  # removes also trace from enabled_traces if all activities are done
                    if trace_id in self.enabled_traces:
                        if self.enabled_traces[trace_id][0]['status'] == 'free':
                            self._allocate_activity(trace_id)
                    self.allocator.resources, self.enabled_traces = proceed_resources(self.current_time, self.enabled_traces, self.allocator.resources)
            self._update_progress_bar()
        self.bar.finish()

        return self.results
