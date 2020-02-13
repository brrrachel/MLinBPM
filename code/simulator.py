import progressbar
import datetime
from dateutil.parser import parse
from utils import get_earliest_trace, compute_timedelta, parse_timedelta, get_available_resources, get_num_of_busy_resources
import statistics


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
        for trace_key in self.trace_ids:
            if parse(data[trace_key]['start']) <= current_time:
                self.results[trace_key] = []
                self.enabled_traces[trace_key] = list(data[trace_key]['events'])
                self.trace_ids.remove(trace_key)

    def _remove_activity_from_trace(self, trace_id):
        self.enabled_traces[trace_id][0]['end'] = self.current_time
        self.enabled_traces[trace_id][0]['duration'] = self.current_time - self.enabled_traces[trace_id][0]['start']
        print(self.enabled_traces[trace_id][0]['duration'])
        resource_id = self.enabled_traces[trace_id][0]['resource']
        self.enabled_traces[trace_id][0]['costs'] = self.allocator.resources[resource_id].salary / 3600 * self.enabled_traces[trace_id][0]['duration'].total_seconds()
        print(self.allocator.resources[resource_id].salary, self.enabled_traces[trace_id][0]['duration'].total_seconds(), self.enabled_traces[trace_id][0]['costs'])
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

    def _proceed_resources(self):
        for resource_id in self.allocator.resources:
            if self.allocator.resources[resource_id].workload > 0:
                finished = self.allocator.resources[resource_id].proceed_activity(self.current_time)
                if finished:
                    self.enabled_traces[self.allocator.resources[resource_id].trace_id][0]['status'] = 'done'
                    self.allocator.resources[resource_id].set_as_free()

    def _update_progress_bar(self):
        self.progressbar_widgets[1] = self.current_time.__str__()
        amount_of_finished = 0
        for trace_key in self.results.keys():
            if trace_key not in self.enabled_traces and trace_key != 'workload' :
                amount_of_finished += 1
        self.bar.update(amount_of_finished)
        self.current_time += self.interval

    def start(self, allocator, data):

        total_duration = []
        for trace_id in data.keys():
            for event in data[trace_id]['events']:
                total_duration.append((parse_timedelta(event['duration'])).total_seconds())
        print("max-duration", compute_timedelta(max(total_duration)))
        print("min-duration", compute_timedelta(min(total_duration)))
        print("median-duration", compute_timedelta(statistics.median(total_duration)))
        print("mean-duration", compute_timedelta(statistics.mean(total_duration)))

        self.allocator = allocator
        self.trace_ids = list(data.keys())
        self.current_time = parse(get_earliest_trace(data)['start']) - self.interval
        self.progressbar_widgets = [
            ' (Simulation Time: ', self.current_time.__str__(), '/', self.end, ') ',
            progressbar.Bar(marker='#'), progressbar.SimpleProgress(),
            ' Finished Traces (', progressbar.Timer(), ') ',
        ]

        self.results['workload'] = {}

        print('--------------------------------------------------------------------------')
        self.bar = progressbar.ProgressBar(maxval=len(self.trace_ids), redirect_stdout=True, widgets=self.progressbar_widgets)
        self.bar.start()
        while len(self.enabled_traces) > 0 or len(self.trace_ids) > 0:
            self.results['workload'][str(self.current_time)] = get_num_of_busy_resources(self.allocator.resources)
            self._search_for_new_traces(data, self.current_time)
            if list(self.enabled_traces.keys()):
                for trace_id in list(self.enabled_traces.keys()):
                    if self.enabled_traces[trace_id][0]['status'] == 'done':
                        self._remove_activity_from_trace(trace_id)  # removes also trace from enabled_traces if all activities are done
                    if trace_id in self.enabled_traces and self.enabled_traces[trace_id][0]['status'] == 'free':
                        self._allocate_activity(trace_id)
            self._proceed_resources()
            self._update_progress_bar()
        self.bar.finish()

        return self.results
