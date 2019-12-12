from dataLoader import load_data, preprocess, get_cases
from utils import get_test_samples
from qValue import QValueAllocator

if __name__ == '__main__':

    data = preprocess(load_data())
    cases = get_cases(data)

    print("Data Loaded")

    training_data, prediction_cases = get_test_samples(data)

    allocator = QValueAllocator()
    print('Train Model')
    allocator.fit(training_data, {})
    print('Allocate Cases')
    pred = allocator.predict(prediction_cases)

    print('Finished')
