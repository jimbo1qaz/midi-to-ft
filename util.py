"""
This file contains miscellaneous utilities. Anything working on a track is excluded.
"""

import bisect as _bisect
from fractions import Fraction as _Fraction

from midi import MIDI as _MIDI
from typing import Sequence as _Sequence, Any as _Any

_TrackType = None

# from types import ModuleType
# import itertools


# These functions should remain static if MidiBackend is ever made a class.

# def printerr(*objects, sep=' ', end='\n', flush=False):
#     print(*objects, sep=sep, end=end, flush=flush)
#     # print(*objects, sep=sep, end=end, flush=flush, file=sys.stderr)

printerr = print


class _IterGetter(_Sequence[_Any]):
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


def insert_sorted(ls: _TrackType, event):
    """ Inserts event at beginning of tick. """

    keyf = lambda ev: ev[1]

    keys = _IterGetter(ls, keyf)
    new_key = keyf(event)

    # TODO: lol why bother bisecting when we do O(n) insert?
    idx = _bisect.bisect_left(keys, new_key)

    ls.insert(idx, event)




def parse_frac(infrac):
    if type(infrac) == str:
        slash_pos = infrac.find('/')
        if slash_pos != -1:
            num = infrac[:slash_pos]
            den = infrac[slash_pos + 1:]
            return _Fraction(num) / _Fraction(den)

    return _Fraction(infrac)


# def ticks2str(ticks, tickrate):
#     time_frac = _Fraction(ticks) / tickrate
#
#     measures = time_frac // 4
#     beats = int(time_frac) % 4
#     remainder = time_frac - (4 * measures) - beats
#     return '{!s:<8}{!s:<8}{!s:<8}'.format(measures, beats, remainder)


def time2ticks(time:str, tickrate):
    # Converts a string representation of time to ticks.

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

    out_beats = 4 * measures + beats + other_frac
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
    if index < 0: raise ValueError('cannot get negative substring')
    if index == 0: return ''

    num_items = len(in_str.split(character))
    if index >= num_items: return in_str

    # wtf pep8
    return in_str.rsplit(sep=character, maxsplit = num_items - index)[0]


'''
>>> s = 'a b c'
>>> skip_spaces(s, 1)   [1:]
'b c'
>>> keep_leading(s, 1)  [:1]
'a'
'''


def channel2num(channel_name):
    return int(float(channel_name) + 0.25)

def instr2num(inst_name):
    return dict_find(inst_name, _MIDI.Number2patch)


def num2instr(patch_num):
    return dict_loose(patch_num, _MIDI.Number2patch)


def instr_fmt(instr_num, is_perc):
    if is_perc:
        name = 'Percussion'
    else:
        name = num2instr(instr_num)

    if instr_num in range(0, 128):
        return '{} {}'.format(instr_num, name)
    else:
        return str(instr_num)



def perc2pitch(perc_name):
    return dict_find(perc_name, _MIDI.Notenum2percussion)


def pitch2perc(pitch):
    return dict_loose(pitch, _MIDI.Notenum2percussion)


def pitch_fmt(pitch):
    if pitch in range(0, 128):
        return '{} {}'.format(pitch, pitch2perc(pitch))
    else:
        return str(pitch)



def dict_find(value, dic):
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

        raise Exception

    return inverse[vmatch[0]]


def dict_loose(key, dic):
    """
    @type key: int
    @type dic: dict
    :return: str
    """
    return dic.get(key, str(key))


def validate_127(name, val):
    if val not in range(0, 128):
        raise Exception('Invalid %s %s not in [0, 127]' % (name, val))


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
        raise Exception('Volume/velocity overflow')
        # printerr('Error: Volume/velocity overflow!')
        # new_volume = 127

    if new_volume < 0:
        raise Exception('Volume/velocity underflow')
        # printerr('Error: Volume/velocity underflow')
        # new_volume = 0

    return new_volume


def grouper(iterable, n):
    """Collect data into fixed-length chunks or blocks"""
    # grouper('ABCDEFG', 3, 'x') --> ABC DEF Gxx"
    length = len(iterable)
    if length % n != 0:
        raise Exception('Grouper error ({} not a multiple of {})!'.format(
            length, n))
    args = [iter(iterable)] * n
    return zip(*args)


# Too lazy to list-comprehension.
# Because [True, True] & [True, False] ==> [True, False] is not valid syntax.
# And importing numpy for a MIDI processing library would be ridiculous.
def andf(l1, l2):
    return [a & b for a, b in zip(l1, l2)]

def lminus(l, m):
    m = set(m)
    return [x for x in l if x not in m]


def num_ints(split):
    for i, sub in enumerate(split):
        if not sub.isnumeric():
            return i

    # ****: default return convention?
    # I think this was meant for variadic @msh where you pass in multiple ints AND an expression.

    return len(split)
    # return None


def copy2d(a):
    return [l[:] for l in a]


def remove_ext(path:str):
    return path[:path.rfind('.')]


def all_same(iterable):
    return iterable.count(iterable[0]) == len(iterable)


from importlib import import_module as importf

assert importf




def ats(arr, indexes):
    return [arr[i] for i in indexes]

