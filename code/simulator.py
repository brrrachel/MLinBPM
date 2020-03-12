import progressbar
import datetime
from dateutil.parser import parse
from utils import get_earliest_trace, compute_timedelta, parse_timedelta, get_num_of_busy_resources


class Simulator:

    allocator = None
    trace_ids = None
    enabled_traces = {}
    results = {}

    # properties of the progress bar
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
            # if the start time of a trace has occurred
            if parse(data[trace_key]['start']) <= current_time:
                self.results[trace_key] = []
                self.enabled_traces[trace_key] = list(data[trace_key]['events'])
                self.trace_ids.remove(trace_key)

    def _remove_activity_from_trace(self, trace_id):
        # is called when all activity instances of a trace is finished
        self.enabled_traces[trace_id][0]['end'] = self.current_time
        self.enabled_traces[trace_id][0]['duration'] = self.current_time - self.enabled_traces[trace_id][0]['start']
        resource_id = self.enabled_traces[trace_id][0]['resource']
        self.enabled_traces[trace_id][0]['costs'] = self.allocator.resources[resource_id].salary / 3600 * self.enabled_traces[trace_id][0]['duration'].total_seconds()
        self.results[trace_id].append(self.enabled_traces[trace_id][0])
        self.enabled_traces[trace_id].pop(0)

        # if all activity instances of the trace are finished, remove the complete trace
        if len(self.enabled_traces[trace_id]) == 0:
            self.enabled_traces.pop(trace_id)

    def _allocate_activity(self, trace_id):
        # is called when the first activity of a trace is free and should be allocated

        # searches for a fitting resource and returns the new status as well the belonging resource id
        new_status, resource_id = self.allocator.allocate_resource(trace_id, self.enabled_traces[trace_id][0])
        self.enabled_traces[trace_id][0]['status'] = new_status
        self.enabled_traces[trace_id][0]['resource'] = resource_id

        # if in the previous step a fitting resource is found, set the start time of the activity instance in trace
        if self.enabled_traces[trace_id][0]['status'] == 'busy':
            self.enabled_traces[trace_id][0]['start'] = self.current_time
            activity_instance = self.enabled_traces[trace_id][0]['activity']
            workload = str(self.allocator.resources[resource_id].workload)
            print(self.current_time.__str__(), ": Resource " + resource_id + " allocated for activity '" + activity_instance + "' of trace " + trace_id + " and has now a workload of " + workload + ".")

    def _proceed_resources(self):
        # is called to proceed in time
        for resource_id in self.allocator.resources:

            # for each busy resource proceed its current execution
            if self.allocator.resources[resource_id].workload > 0:
                finished = self.allocator.resources[resource_id].proceed_activity(self.current_time)

                if finished:
                    # change status of resource and set as free
                    self.enabled_traces[self.allocator.resources[resource_id].trace_id][0]['status'] = 'done'
                    self.allocator.resources[resource_id].set_as_free()

    def _update_progress_bar(self):
        # updates the visualization in the terminal
        self.progressbar_widgets[1] = self.current_time.__str__()
        amount_of_finished = 0
        for trace_key in self.results.keys():
            if trace_key not in self.enabled_traces and trace_key != 'workload':
                amount_of_finished += 1
        self.bar.update(amount_of_finished)
        self.current_time += self.interval

    def start(self, allocator, data):
        # start the simulation

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

        # while there are running traces or not all traces were already startet
        while len(self.enabled_traces) > 0 or len(self.trace_ids) > 0:

            # evaluate currently working resources
            self.results['workload'][str(self.current_time)] = get_num_of_busy_resources(self.allocator.resources)

            self._search_for_new_traces(data, self.current_time)

            # for running traces
            if list(self.enabled_traces.keys()):
                for trace_id in list(self.enabled_traces.keys()):

                    # if the first activity instance in trace is finished
                    if self.enabled_traces[trace_id][0]['status'] == 'done':
                        # removes also trace from enabled_traces if all activity instances are finished
                        self._remove_activity_from_trace(trace_id)

                    # if the trace has activity instances left and the first activity instance in trace is not allocated
                    if trace_id in self.enabled_traces and self.enabled_traces[trace_id][0]['status'] == 'free':
                        self._allocate_activity(trace_id)

            self._proceed_resources()
            self._update_progress_bar()

        self.bar.finish()
        return self.results
