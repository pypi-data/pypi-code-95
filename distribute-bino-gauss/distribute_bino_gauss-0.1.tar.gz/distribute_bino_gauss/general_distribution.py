class Distribution:
    def __init__(self, mu=0, sigma=1):
        self.mean = mu
        self.stdev = sigma
        self.data = []

    def read_data_file(self, filename):
        with open(filename) as f:
            numbers = f.read().split('\n')
            numbers = [int(value) for value in numbers]

        self.data = numbers


# test = Distribution(25, 2)
# print(test)
# test.read_data_file('numbers.txt')
# print(test)
