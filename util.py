"""
This file contains miscellaneous utilities. Anything working on a track is excluded.
"""
import bisect
from fractions import Fraction as _Fraction
from tkinter import *
from tkinter import ttk, font
from types import FunctionType
from typing import List

EventType = List
TrackType = List[EventType]

epsilon = 0.000001

class MidiException(Exception):
    pass


class IterGetter:
    """
    bisect does not provide "key" because repeatedly calling "key" is inefficient. like I care?

    I'm calling this function once per list, tops. O(N) generation is SLOWER than O(log N) bisection!
    """

    def __init__(self, ls, keyf):
        self.ls = ls
        self.keyf = keyf

    def __len__(self):
        return len(self.ls)

    def __getitem__(self, index):
        return self.keyf(self.ls[index])


def idx_time(ls: TrackType, time: int):
    keyf = lambda ev: ev[1]

    times = IterGetter(ls, keyf)

    idx = bisect.bisect_left(times, time)
    return idx




def parse_frac(infrac):
    if type(infrac) == str:
        slash_pos = infrac.find('/')
        if slash_pos != -1:
            num = infrac[:slash_pos]
            den = infrac[slash_pos + 1:]
            return _Fraction(num) / _Fraction(den)

    return _Fraction(infrac)


def time2ticks(time: str, tickrate, keysig=4):
    # Converts a string timestamp to ticks.

    # measures : beats : beat frac T ticks

    splitted = time.split(':')

    # Get measures.
    measures = _Fraction(splitted[0])

    # Get beats (qnote).
    beats = 0
    if len(splitted) >= 2:
        beats = _Fraction(splitted[1])

    # Get partial beats.
    other_frac = 0
    if len(splitted) >= 3:
        other = splitted[2]
        other_frac = parse_frac(other)

    # Get ticks.
    ticks = 0
    tsplit = time.lower().split('t')
    if len(tsplit) > 1:
        ticks = int(tsplit[1])

    out_beats = keysig * measures + beats + other_frac
    out_ticks = round(out_beats * tickrate) + ticks

    return out_ticks


def skip_spaces(in_str, index, character=None):
    """
    @type in_str: str
    @type index: int
    """

    if index < 0:
        raise ValueError('cannot exclude negative substring')

    splitted = in_str.split(sep=character, maxsplit=index)
    if index < len(splitted):
        return splitted[index]
    return ''


def keep_leading(in_str, index, character=None):
    """
    >>> s = 'a b c'
    >>> skip_spaces(s, 1)   #[1:]
    'b c'
    >>> keep_leading(s, 1)  #[:1]
    'a'
    """
    if index < 0: raise ValueError('cannot get negative substring')
    if index == 0: return ''

    num_items = len(in_str.split(character))
    if index >= num_items:
        return in_str
    return in_str.rsplit(sep=character, maxsplit=num_items-index)[0]




def dict_getkey(value, dic):
    value = value.replace('_', ' ').lower()

    # # Is it an instrument number?
    # if isinstance(value, _numbers.Number) or value.isnumeric():
    #     return int(value)
    try:
        return int(value)
    except (ValueError, TypeError):
        pass

    # We know it's an instrument name.

    vals = map(lambda val: val.lower(), dic.values())

    # Look for perfect matches.

    inverse = {val.lower(): key for key, val in dic.items()}
    if value in inverse:
        return inverse[value]

    # We know there are no perfect matches.
    # If there are multiple matches, then error out.

    vmatch = list(filter(lambda val: value in val, vals))
    vmatch.sort(key=len)

    if len(vmatch) != 1:
        print('Invalid name: {}'.format(value))
        print('{} matches:'.format(len(vmatch)))
        for match in vmatch:
            print(match)
        print('Exact matches will NOT trigger this error, try extending?')

        raise MidiException

    return inverse[vmatch[0]]


def dict_get(key, dic):
    """
    @type key: int
    @type dic: dict
    :return: str
    """
    return dic.get(key, str(key))


def validate_127(name, val):
    if val not in range(0, 128):
        raise MidiException('Invalid %s %s not in [0, 127]' % (name, val))


def clip_127(in_val):
    # Returns a value, error_str tuple.
    if in_val > 127:
        return 127, 1
    if in_val < 0:
        return 0, -1
    return in_val, 0

def volume_calc(a, b):
    new_volume = round(a * b)

    if new_volume > 127:
        raise MidiException('Volume/velocity overflow')
        # printerr('Error: Volume/velocity overflow!')
        # new_volume = 127

    if new_volume < 0:
        raise MidiException('Volume/velocity underflow')
        # printerr('Error: Volume/velocity underflow')
        # new_volume = 0

    return new_volume



def remove_ext(path:str):
    return path[:path.rfind('.')]


def I(s, *args, **kwargs):
    return [int(x, *args, **kwargs) for x in s.split()]


from importlib import import_module as importf

assert importf




def ats(arr, indexes):
    return [arr[i] for i in indexes]


class AttrDict(dict):
    def __init__(self, seq=None, **kwargs):
        if seq is None:
            seq = {}
        super(self.__class__, self).__init__(seq, **kwargs)
        self.__dict__ = self


# **** GUI ****

MONO_FONT = '"DejaVu Sans Mono" 9'
# s = ttk.Style()
# s.configure('TCombobox', font=MONO_FONT)

# MONO_FONT = font.Font(family="DejaVu Sans Mono", size=9)

zeros = (0, 0, 0, 0)
nsew = 'nsew'


def grid(widget: Widget, x=0, y=0, **kwargs):
    widget.grid(column=x, row=y, **kwargs)


def weigh(frame, xs=[1], ys=[1]):
    for row, weight in enumerate(ys):
        frame.rowconfigure(row, weight=weight)

    for column, weight in enumerate(xs):
        frame.columnconfigure(column, weight=weight)


def y_weigh(frame: ttk.Frame, ys):
    weigh(frame, ys=ys, xs=[1])


def recursive_bind(bound_widget: Widget, sequence: str, func):
    """
    Every event is captured, but only applied if the event's widget is within
    the binding.
    """

    root = bound_widget._root()

    def root_func(event: Event):
        clicked = event.widget  # Clicked
        while clicked:
            if clicked == bound_widget:
                return func(event)
            clicked = clicked.master
        return

    root.bind(sequence, root_func)
