import subprocess
from datetime import datetime
from io import BytesIO
from os import path
import shutil
from typing import Callable, Iterable, Optional, TypeVar
from string import Formatter


def coords(lon, lat):
    t = "%2.4f" % lat
    if (lat > 0):
        t += "N"
    else:
        t += "S"

    t += " %2.4f" % lon
    if (lon > 0):
        t += "E"
    else:
        t += "W"
    return t


def make_thumbnail(input_path, output_path, width=200):
    subprocess.check_call(["convert", "-thumbnail", str(width), input_path, output_path])


T = TypeVar("T")


def first(condition: Callable[[T], bool], items: Iterable[T]) -> Optional[T]:
    '''Return first element for which @condition is True. Otherwise return None'''
    for item in items:
        if condition(item):
            return item
    return None


def get_footer():
    """Returns data regarding the last update: timestamp of the upgrade process and SHA of the last git commit.
       Both pieces of information are coming from the timestamp.txt file (which is generated by update.sh script)"""
    COMMIT_FILE = "commit.txt"
    try:
        root_dir = path.dirname(path.realpath(__file__))
        root_dir = path.dirname(root_dir)
        commit_path = path.join(root_dir, COMMIT_FILE)

        with open(commit_path, 'r') as f:
            return {
                'commit': f.read().strip(),
                'timestamp': datetime.fromtimestamp(path.getmtime(commit_path)).isoformat(" ", "minutes")
            }
    except OSError:
        # The file was not found or is generally inaccessible. Return nothing.
        return None


def save_binary_stream_to_file(path: str, stream: BytesIO):
    '''Efficient way to save binary stream to file.
        See: https://stackoverflow.com/a/39050559'''
    stream.seek(0)
    with open(path, 'wb') as f:
        shutil.copyfileobj(stream, f, length=131072)


def strfdelta(tdelta, fmt='{D:02}d {H:02}h {M:02}m {S:02}s', inputtype='timedelta'):
    """Convert a datetime.timedelta object or a regular number to a custom-
    formatted string, just like the stftime() method does for datetime.datetime
    objects.

    The fmt argument allows custom formatting to be specified.  Fields can
    include seconds, minutes, hours, days, and weeks.  Each field is optional.

    Some examples:
        '{D:02}d {H:02}h {M:02}m {S:02}s' --> '05d 08h 04m 02s' (default)
        '{W}w {D}d {H}:{M:02}:{S:02}'     --> '4w 5d 8:04:02'
        '{D:2}d {H:2}:{M:02}:{S:02}'      --> ' 5d  8:04:02'
        '{H}h {S}s'                       --> '72h 800s'

    The inputtype argument allows tdelta to be a regular number instead of the
    default, which is a datetime.timedelta object.  Valid inputtype strings:
        's', 'seconds',
        'm', 'minutes',
        'h', 'hours',
        'd', 'days',
        'w', 'weeks'

    by MarredCheese, source: https://stackoverflow.com/questions/538666/
    """

    # Convert tdelta to integer seconds.
    if inputtype == 'timedelta':
        remainder = int(tdelta.total_seconds())
    elif inputtype in ['s', 'seconds']:
        remainder = int(tdelta)
    elif inputtype in ['m', 'minutes']:
        remainder = int(tdelta) * 60
    elif inputtype in ['h', 'hours']:
        remainder = int(tdelta) * 3600
    elif inputtype in ['d', 'days']:
        remainder = int(tdelta) * 86400
    elif inputtype in ['w', 'weeks']:
        remainder = int(tdelta) * 604800

    f = Formatter()
    desired_fields = [field_tuple[1] for field_tuple in f.parse(fmt)]
    possible_fields = ('W', 'D', 'H', 'M', 'S')
    constants = {'W': 604800, 'D': 86400, 'H': 3600, 'M': 60, 'S': 1}
    values = {}
    for field in possible_fields:
        if field in desired_fields and field in constants:
            values[field], remainder = divmod(remainder, constants[field])
    return f.format(fmt, **values)
