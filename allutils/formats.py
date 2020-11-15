from redbot.core.commands import BadArgument
from redbot.core.utils.chat_formatting import inline


class plural:
    def __init__(self, value):
        self.value = value

    def __format__(self, format_spec):
        v = self.value
        singular, sep, plural = format_spec.partition("|")
        plural = plural or f"{singular}s"
        if abs(v) != 1:
            return f"{v} {plural}"
        return f"{v} {singular}"


def human_join(seq, delim=", ", final="or"):
    size = len(seq)
    if size == 0:
        return ""

    if size == 1:
        return seq[0]

    if size == 2:
        return f"{seq[0]} {final} {seq[1]}"

    return delim.join(seq[:-1]) + f" {final} {seq[-1]}"


class TabularData:
    def __init__(self):
        self._widths = []
        self._columns = []
        self._rows = []

    def set_columns(self, columns):
        self._columns = columns
        self._widths = [len(c) + 2 for c in columns]

    def add_row(self, row):
        rows = [str(r) for r in row]
        self._rows.append(rows)
        for index, element in enumerate(rows):
            width = len(element) + 2
            if width > self._widths[index]:
                self._widths[index] = width

    def add_rows(self, rows):
        for row in rows:
            self.add_row(row)

    def render(self):
        """Renders a table in rST format.

        Example:

        +-------+-----+
        | Name  | Age |
        +-------+-----+
        | Alice | 24  |
        |  Bob  | 19  |
        +-------+-----+
        """

        sep = "+".join("-" * w for w in self._widths)
        sep = f"+{sep}+"

        to_draw = [sep]

        def get_entry(d):
            elem = "|".join(f"{e:^{self._widths[i]}}" for i, e in enumerate(d))
            return f"|{elem}|"

        to_draw.append(get_entry(self._columns))
        to_draw.append(sep)

        for row in self._rows:
            to_draw.append(get_entry(row))

        to_draw.append(sep)
        return "\n".join(to_draw)


def positive_int(arg: str) -> int:
    arg = arg.replace(",", "")
    arg = arg.replace(" ", "")
    arg = arg.replace("k", "000")
    arg = arg.replace("million", "000000")
    arg = arg.replace("mil", "000000")
    arg = arg.replace("m", "000000")
    try:
        ret = int(arg)
    except ValueError:
        raise BadArgument("{arg} is not an integer.".format(arg=inline(arg)))
    if ret <= 0:
        raise BadArgument("{arg} is not a positive integer.".format(arg=inline(arg)))
    if ret >= 10000000000:
        raise BadArgument(
            "{arg} is no where near an amount of coins you'll reach, idiot".format(arg=inline(arg))
        )
    return ret


def hundred_int(arg: str):
    try:
        ret = int(arg)
    except ValueError:
        raise BadArgument("{arg} is not an integer.".format(arg=inline(arg)))
    if ret < 0 or ret > 100:
        raise BadArgument(f"`{arg}` must be an integer between 0 and 100.")
    return ret
