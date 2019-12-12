

def _get_cases(data):
    cases = set()

    for trace in data.keys():
        cases.add(tuple([event['activity'] for event in data[trace]['events']]))

    return cases


def get_test_samples(data):
    return data, _get_cases(data)
