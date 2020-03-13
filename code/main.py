from dataLoader import load_data, limit_data
from plotting import skills_distribution_plotting, overall_workload_plotting, allocation_trace_duration_plotting
from simulator import Simulator
from allocator.greedy import GreedyAllocator
from allocator.qValue import QValueAllocator
from allocator.qValueMultiDimension import QValueAllocatorMultiDimension
import datetime
from utils import compute_timedelta, parse_timedelta, calculate_salaries
from optparse import OptionParser
import json

if __name__ == '__main__':

    # declare all options
    parser = OptionParser()
    parser.add_option("-g", dest="greedy", help="Run Greedy Allocator", action="store_true", default=False)
    parser.add_option("-q", dest="q_value", help="Run QValue Allocator", action="store_true", default=False)
    parser.add_option("-m", dest="q_value_multi", help="Run QValue Allocator with additional salary dimension", action="store_true", default=False)
    parser.add_option("-w", dest="workload", help="Set Workload for Allocator, default = 1", action="store", default=1, type="int")
    parser.add_option("-i", dest="interval", help="Interval steps for simulation [Seconds], default = 60 = 00:01 h", default=60, type="int", action="store")
    parser.add_option("-s", "--start", dest="start", help="Set Start date to limit data [YYYY/MM/DD], default = 2012/10/01", action="store", default="2012/10/01", type="str")
    parser.add_option("-e", "--end", dest="end", help="Set Start date to limit data [YYYY/MM/DD], default = 2012/11/15", action="store", default="2012/11/15", type="str")
    parser.add_option("-t", dest="threshold", help="Threshold for min occurrence of an activity in the whole dataset, default = 0.0017", default=0.0017, type="float", action="store")
    parser.add_option("-u", dest="threshold_traces", help="Threshold for min occurrence of an activity in traces, default = 0.005", default=0.005, type="float", action="store")
    (options, args) = parser.parse_args()

    # load and preprocess data
    print('Selected Thresholds: ' + str(options.threshold) + " and " + str(options.threshold_traces))
    data, original_data = load_data(options.threshold, options.threshold_traces)

    # limit data
    start = datetime.datetime.strptime(options.start, "%Y/%m/%d")
    end = datetime.datetime.strptime(options.end, "%Y/%m/%d")
    limited_data = limit_data(data, start, end)

    print('Data Loaded')

    # calculate salary
    salary = calculate_salaries(data)
    skills_distribution_plotting(salary)

    # initialize the allocator
    allocator = None
    allocator_name = None
    if options.q_value and options.q_value_multi or options.q_value and options.greedy or options.greedy and options.q_value_multi or options.q_value and options.q_value_multi and options.greedy:
        print('You chose to many allocators. Please choose only one of the following: -g for greedy, -q for standard qValue or -m for qValue with additional salary dimension')
    if options.q_value:
        print('Using QValueAllocator with workload ' + str(options.workload))
        allocator = QValueAllocator(options.workload)
        allocator_name = 'QValueAllocator_w' + str(options.workload)
    elif options.q_value_multi:
        print('Using QValueMultiDimensionAllocator with workload ' + str(options.workload))
        allocator = QValueAllocatorMultiDimension(options.workload)
        allocator_name = 'QValueMultiDimensionAllocator_w' + str(options.workload)
    elif options.greedy:
        print('Using GreedyAllocator with workload' + str(options.workload))
        allocator = GreedyAllocator(options.workload)
        allocator_name = 'GreedyAllocator_w' + str(options.workload)

    if allocator is None:
        print("You didn't choose an allocator. Use -g for greedy, -q for standard qValue or -m for qValue with additional salary dimension")
        exit(0)

    print('Train Model')
    allocator.fit(original_data, salary)

    print('Start Allocating')
    results = Simulator(options.interval, options.end).start(allocator, limited_data)

    # evaluate results
    def converter(o):
        if isinstance(o, datetime.datetime) or isinstance(o, datetime.timedelta):
            return o.__str__()
    with open('results/' + str(options.threshold).split('.')[1] + '_' + str(options.threshold_traces).split('.')[1] + '_' + allocator_name + '.json', 'w') as fp:
        json.dump(results, fp, default=converter)
    overall_workload_plotting(results['workload'], options.threshold, options.threshold_traces, str(options.workload), allocator_name.split("_")[0])
    allocation_trace_duration_plotting(results, allocator_name.split("_")[0], options.threshold, options.threshold_traces, str(options.workload))

    print('Finished')
