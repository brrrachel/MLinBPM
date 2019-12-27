from dataLoader import load_data, preprocess
from utils import get_test_samples
from qValue import QValueAllocator
from utils import get_resources

from optparse import OptionParser

if __name__ == '__main__':

    parser = OptionParser()
    parser.add_option("-t", dest="threshold", help="Threshold for min occurence of an activity in the whole dataset", default=0.019, type="float", action="store")
    parser.add_option("-q", dest="q_value", help="Run QValue Allocator", action="store_true", default=True)
    (options, args) = parser.parse_args()

    print('Selected Threshold: ', options.threshold)
    data = load_data(options.threshold)
    print('Data Loaded')

    training_data, prediction_cases = get_test_samples(data)

    allocator = None

    if options.q_value:
        print('Using QValueAllocator')
        allocator = QValueAllocator()
        resources = get_resources(data)
        for resource in resources:
            allocator.add_resource(resource)

    print('Train Model')
    allocator.fit(training_data)
    print('Allocate Cases')
    pred = allocator.predict(prediction_cases)

    print('Finished')
