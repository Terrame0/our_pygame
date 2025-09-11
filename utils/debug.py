from utils.classproperty import classproperty


class debug:
    indentation_level = 0
    is_enabled = True
    after_indent = False
    indent_size = 3

    @classproperty
    def enable(cls):
        cls.is_enabled = True

    @classproperty
    def disable(cls):
        cls.is_enabled = False

    @staticmethod
    def log(string):
        pass
        if debug.is_enabled:
            char = "│"
            if debug.after_indent:
                char = "╿"
                debug.after_indent = False
            indent = "[log]: " + "".join(
                [f"{char}" + " " * debug.indent_size] * debug.indentation_level
            )
            print(indent + str(string))

    @staticmethod
    def indent():
        debug.after_indent = True
        debug.indentation_level += 1

    @staticmethod
    def dedent():
        debug.indentation_level -= 1
        debug.log("╰" + "─" * debug.indent_size + ">")
