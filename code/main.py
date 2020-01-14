from dataLoader import load_data, preprocess
from allocator.qValue import QValueAllocator
from allocator.qValueWorkload import QValueAllocatorWorkload
from allocator.greedy import GreedyAllocator

from optparse import OptionParser

if __name__ == '__main__':

    parser = OptionParser()
    parser.add_option("-t", dest="threshold", help="Threshold for min occurence of an activity in the whole dataset", default=0.0017, type="float", action="store")
    parser.add_option("-g", dest="greedy", help="Run Greedy Allocator", action="store_true", default=True)
    parser.add_option("-q", dest="q_value", help="Run QValue Allocator", action="store_true", default=False)
    (options, args) = parser.parse_args()

    print('Selected Threshold: ', options.threshold)
    data = load_data(options.threshold)
    print('Data Loaded')

    allocator = None
    if options.q_value:
        print('Using QValueAllocator')
        allocator = QValueAllocatorWorkload()
    elif options.greedy:
        print('Using GreedyAllocator')
        allocator = GreedyAllocator()

    print('Train Model')
    allocator.fit(data)
    print('Allocate Cases')
    allocator.predict(data)

    print('Finished')
