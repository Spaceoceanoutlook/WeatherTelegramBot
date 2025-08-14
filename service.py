class Counter:
    def __init__(self):
        self.count = 0

    def __call__(self):
        self.count += 1

    def get(self):
        return self.count
