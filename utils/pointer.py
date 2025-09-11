class ptr:
    def __init__(self, contents):
        self.contents = contents

    def __invert__(self):
        return self.contents