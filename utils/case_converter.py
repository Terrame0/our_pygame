import re

_PATTERN = re.compile(r'(?<!^)(?=[A-Z])')
def pascal_to_snake(pascal_str):
    return _PATTERN.sub('_', pascal_str).lower()