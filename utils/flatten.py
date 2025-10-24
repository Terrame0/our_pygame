
# -- flattens any iterable
def flatten(obj):
    # -- set to track visited container ids to prevent infinite recursion
    memo = set()

    def inner_flatten(current):
        # -- handle strings/bytes as atomic elements (don't split)
        if isinstance(current, (str, bytes, bytearray)):
            yield current
            return

        # -- prevent recursion on cyclic containers
        if id(current) in memo:
            yield current
            return

        # -- attempt iteration if possible
        try:
            iterable = iter(current)
        except TypeError:
            # -- not iterable: treat as leaf element
            yield current
            return

        # -- mark container as visited
        memo.add(id(current))
        try:
            for item in iterable:
                # -- recursively flatten each item
                yield from inner_flatten(item)
        finally:
            # -- unmark container after processing
            memo.remove(id(current))

    # -- initiate the flattening process
    yield from inner_flatten(obj)