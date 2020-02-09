from dataLoader import load_data, limit_data
from plotting import allocation_duration_plotting, resource_workload_plotting, activity_occurence_histogram, plot_workload, input_data_duration_plotting, trace_duration_plotting
from simulator import Simulator
from allocator.greedy import GreedyAllocator
from allocator.qValue import QValueAllocator
from allocator.qValueMultiDimension import QValueAllocatorMultiDimension
import datetime
from utils import compute_timedelta, parse_timedelta, calculate_salaries
import statistics
from optparse import OptionParser
import json

if __name__ == '__main__':

    parser = OptionParser()
    parser.add_option("-t", dest="threshold", help="Threshold for min occurence of an activity in the whole dataset", default=0.0017, type="float", action="store")
    parser.add_option("-u", dest="threshold_traces", help="Threshold for min occurence of an activity in traces", default=0.005, type="float", action="store")
    parser.add_option("-i", dest="interval", help="Interval steps for simulation [Seconds], default = 1800 = 00:30 h", default=1800, type="int", action="store")
    parser.add_option("-g", dest="greedy", help="Run Greedy Allocator", action="store_true", default=False)
    parser.add_option("-q", dest="q_value", help="Run QValue Allocator", action="store_true", default=False)
    parser.add_option("-m", dest="q_value_multi", help="Run QValue Allocator with additional salary dimension", action="store_true", default=False)
    parser.add_option("-w", dest="q_value_workload", help="Set Workload of Q_Value Allocator", action="store", default=1, type="int")
    parser.add_option("-s", "--start", dest="start", help="Set Start date to limit data [YYYY/MM/DD], default = 2010/07/01", action="store", default="2010/07/01", type="string")
    parser.add_option("-e", "--end", dest="end", help="Set End date to limit data [YYYY/MM/DD], default = 2015/02/15", action="store", default="2015/02/15", type="string")
    (options, args) = parser.parse_args()

    print('Selected Thresholds: ' + str(options.threshold) + " and " + str(options.threshold_traces))
    data, original_data = load_data(options.threshold, options.threshold_traces)

    start = datetime.datetime.strptime(options.start, "%Y/%m/%d")
    end = datetime.datetime.strptime(options.end, "%Y/%m/%d")
    limited_data = limit_data(data, start, end)
    print('Data Loaded')

    salary = calculate_salaries(data)
    activity_occurence_histogram(salary)

    # total_duration = []
    # for trace_id in original_data.keys():
    #     for event in original_data[trace_id]['events']:
    #         total_duration.append((parse_timedelta(event['duration'])).total_seconds())
    # print("max-duration", compute_timedelta(max(total_duration)))
    # print("min-duration", compute_timedelta(min(total_duration)))
    # print("median-duration", compute_timedelta(statistics.median(total_duration)))
    # print("mean-duration", compute_timedelta(statistics.mean(total_duration)))

    allocator = None
    allocator_name = None
    if options.q_value and options.q_value_multi or options.q_value and options.greedy or options.greedy and options.q_value_multi or options.q_value and options.q_value_multi and options.greedy:
        print('You chose to many allocators. Please choose only one of the following: -g for greedy, -q for standard qValue or -m for qValue with additional salary dimension')
    if options.q_value:
        print('Using QValueAllocator with workload ' + str(options.q_value_workload))
        allocator = QValueAllocator(options.q_value_workload)
        allocator_name = 'QValueAllocator_w' + str(options.q_value_workload)
    elif options.greedy:
        print('Using GreedyAllocator')
        allocator = GreedyAllocator(options.q_value_workload)
        allocator_name = 'GreedyAllocator_w' + str(options.q_value_workload)
    elif options.q_value_multi:
        print('Using QValueMultiDimensionAllocator')
        allocator = QValueAllocatorMultiDimension(options.q_value_workload)
        allocator_name = 'QValueMultiDimensionAllocator'

    if allocator is None:
        print("You didn't choose a allocator. Use -g for greedy, -q for standard qValue or -m for qValue with additional salary dimension")
        exit(0)

    # input_data_duration_plotting(limited_data, options.threshold, options.threshold_traces)

    print('Train Model')
    allocator.fit(original_data, salary)
    print('Allocate Cases')
    results = Simulator(options.interval, options.end).start(allocator, limited_data)

    # evaluate results
    def converter(o):
        if isinstance(o, datetime.datetime) or isinstance(o, datetime.timedelta):
            return o.__str__()
    with open('results/' + str(options.threshold).split('.')[1] + '_' + str(options.threshold_traces).split('.')[1] + '_' + allocator_name + '.json', 'w') as fp:
        json.dump(results, fp, default=converter)
    # allocation_duration_plotting(results, allocator_name, options.threshold)
    # resource_workload_plotting(results, allocator_name, options.threshold, options.threshold_traces)
    plot_workload(results['workload'], options.threshold, options.threshold_traces, options.q_value_workload, allocator_name.split("_")[0])
    trace_duration_plotting(results, allocator_name.split("_")[0], options.threshold, options.threshold_traces, options.q_value_workload)

    print('Finished')
