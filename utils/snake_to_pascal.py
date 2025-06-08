import re


def snake_to_pascal(snake_str):
    return re.sub(r"(?:^|_)([a-zA-Z])", lambda m: m.group(1).upper(), snake_str)