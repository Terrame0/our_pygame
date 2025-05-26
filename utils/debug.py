from utils.singleton_decorator import singleton


class debug:
    indentation_level = 0

    @staticmethod
    def log(string: str):
        indent = "".join(["|   "] * debug.indentation_level)
        print(indent + string)

    @staticmethod
    def indent():
        debug.indentation_level += 1

    @staticmethod
    def dedent():
        debug.indentation_level -= 1