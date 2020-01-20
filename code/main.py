from dataLoader import load_data
from plotting import allocation_duration_plotting, resource_workload_plotting
from allocator.qValueWorkload import QValueAllocatorWorkload
from allocator.greedy import GreedyAllocator
import datetime

from optparse import OptionParser
import json

if __name__ == '__main__':

    parser = OptionParser()
    parser.add_option("-t", dest="threshold", help="Threshold for min occurence of an activity in the whole dataset", default=0.0017, type="float", action="store")
    parser.add_option("-i", dest="interval", help="Interval steps for simulation [Seconds]", default=3600, type="int", action="store")
    parser.add_option("-g", dest="greedy", help="Run Greedy Allocator", action="store_true", default=True)
    parser.add_option("-q", dest="q_value", help="Run QValue Allocator", action="store_true", default=False)
    parser.add_option("-w", dest="q_value_workload", help="Set Workload of Q_Value Allocator", action="store", default=1, type="int")
    (options, args) = parser.parse_args()

    print('Selected Threshold: ', options.threshold)
    data = load_data(options.threshold)
    print('Data Loaded')

    allocator = None
    allocator_name = None
    if options.q_value:
        print('Using QValueAllocator with workload ' + str(options.q_value_workload))
        allocator = QValueAllocatorWorkload(options.q_value_workload)
        allocator_name = 'QValueAllocator_w' + str(options.q_value_workload)
    elif options.greedy:
        print('Using GreedyAllocator')
        allocator = GreedyAllocator()
        allocator_name = 'GreedyAllocator'

    print('Train Model')
    allocator.fit(data)
    print('Allocate Cases')
    results = allocator.predict(data, options.interval)

    # evaluate results
    def converter(o):
        if isinstance(o, datetime.datetime) or isinstance(o, datetime.timedelta):
            return o.__str__()
    with open('results/' + str(options.threshold) + '_' + allocator_name + '.json', 'w') as fp:
        json.dump(results, fp, default=converter)
    allocation_duration_plotting(results, allocator_name, options.threshold)
    resource_workload_plotting(results, allocator_name, options.threshold)

    print('Finished')
