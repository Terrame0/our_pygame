
from utils.classproperty import classproperty


class debug:
    indentation_level = 0
    is_enabled = True

    @classproperty
    def enable_output(cls):
        cls.is_enabled = True

    @classproperty
    def disable_output(cls):
        cls.is_enabled = False

    @staticmethod
    def log(string):
        if debug.is_enabled:
            indent = "".join(["|   "] * debug.indentation_level)
            print(indent + str(string))

    @staticmethod
    def indent():
        debug.indentation_level += 1

    @staticmethod
    def dedent():
        debug.indentation_level -= 1