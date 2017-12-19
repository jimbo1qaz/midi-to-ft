from fractions import Fraction
from enum import Enum, auto, unique
import math
from tkinter import *
from tkinter import ttk
import keyboard
import time

from midiutil import perc2pitch
from util import weigh, grid, nsew, time2ticks, idx_time, epsilon, TrackType,\
    AttrDict, MONO_FONT


class ScrolledText(Text):
    def __init__(self, master=None, **kw):
        self.frame = ttk.Frame(master)
        self.vbar = ttk.Scrollbar(self.frame)
        self.vbar.pack(side=RIGHT, fill=Y)

        kw.update({'yscrollcommand': self.vbar.set})
        Text.__init__(self, self.frame, **kw)
        self.pack(side=LEFT, fill=BOTH, expand=True)
        self.vbar['command'] = self.yview

        # Copy geometry methods of self.frame without overriding Text
        # methods -- hack!
        text_meths = vars(Text).keys()
        methods = vars(Pack).keys() | vars(Grid).keys() | vars(Place).keys()
        methods = methods.difference(text_meths)

        for m in methods:
            if m[0] != '_' and m != 'config' and m != 'configure':
                setattr(self, m, getattr(self.frame, m))

    def __str__(self):
        return str(self.frame)


@unique
class Release(Enum):
    release = auto()
    cut = auto()


class ScriptPanel:
    def __init__(self, frame, app, cfg):
        assert cfg or True
        self.frame = frame
        self.app = app
        weigh(frame, ys=[0,0,0,0,0,0,0,0,0,1])
        frame.configure(padding=4)

        # **** Script configuration ****

        ROW_BEAT = cfg.get('rows_beat', 4)
        self.ft = Famitracker()

        # **** GUI setup ****

        self.text = text = ScrolledText(frame, height=16, font=MONO_FONT)
        grid(text, sticky=nsew, rowspan=1000)

        # self.row_qnote_label =
        grid(Label(frame, text='Rows per beat:'), x=1, sticky=nsew)
        self.row_beat = row_beat = ttk.Entry(frame, width=6)
        row_beat.insert(0, str(ROW_BEAT))
        grid(row_beat, x=2, sticky=nsew)

        text.configure(maxundo=-1)
        text.bind('<Control-Return>', self._send)



    def _send(self, event: Event):
        keyboard.release('ctrl+shift+alt')
        keyboard.press_and_release('alt+tab')

        line = self.text.get('insert linestart', 'insert lineend').strip()  # type: str
        words = line.split()
        it = iter(words)

        # **** Parse text ****
        # 't1 [0 3:2] [perc|release...]'

        trackn = next(it).lstrip('track')
        trackn = int(trackn)

        begin = next(it).lstrip('[')
        begin = time2ticks(begin, self.app.tick_rate)

        end = next(it).rstrip(']')
        end = time2ticks(end, self.app.tick_rate)

        cfg = AttrDict()
        for flag in it:

            # perc=72 -> 0
            # perc=72= -> 72
            if flag.startswith('perc='):
                things = flag.split('=')

                if len(things) == 2:
                    new_note = 0
                elif things[2] == '':
                    new_note = perc2pitch(things[1])
                else:
                    new_note = perc2pitch(things[2])
                in_note = perc2pitch(things[1])

                def mutate(ev, in_note=in_note, new_note=new_note):
                    if ev[4] != in_note:
                        return None
                    ev = ev[:]
                    ev[4] = new_note   # percussion note 0
                    return ev

                cfg.mutate = mutate
                continue

            try:
                cfg.release = Release[flag]
                continue
            except KeyError:
                pass

            cfg[flag] = True

        cfg.rows_per_beat = int(self.row_beat.get())

        # **** MIDI to rows ****

        rows = self.rows_midi(trackn, begin, end, cfg)

        self.ft.send(rows)

        return 'break'

    def rows_midi(self, trackn, begin_midi, end_midi, cfg):
        def row_midi(midi_t, ceil=False):
            rown = Fraction(midi_t - begin_midi) / self.app.tick_rate \
                   * cfg['rows_per_beat']
            if ceil:
                return math.ceil(rown)
            else:
                return round(rown - epsilon)

        nrows = row_midi(end_midi, ceil=False)

        rows = [None] * nrows
        release = cfg.get('release', None)  # type: Release
        # if release:
        #     release = Release[release]  # type: Enum

        row_end = None

        # def on_note(note):
        #     nonlocal row_end

        track = self.app.tracks[trackn]     # type: TrackType
        i0 = idx_time(track, begin_midi)
        i1 = idx_time(track, end_midi)
        mutate = cfg.get('mutate', lambda ev: ev)
        for ev in track[i0:i1]:
            if ev[0] == 'note':
                ev = mutate(ev)
                if not ev:
                    continue

                mtime = ev[1]
                mdur = ev[2]
                mpitch = ev[4]
                # vel = ev[5]

                row_time = row_midi(mtime)
                if row_end is not None and row_end < row_time and not rows[row_end]:
                    rows[row_end] = release
                if release:
                    row_end = row_midi(mtime + mdur)
                    if row_end == row_time:
                        row_end += 1

                rows[row_time] = mpitch

        if row_end is not None and row_end in range(len(rows)) and not rows[row_end]:
            rows[row_end] = release

        return rows


OCTAVE = 12


class Famitracker:
    def __init__(self):
        self.octave_up = 'f11'
        self.octave_down = 'f10'
        self.keyboards = ['zsxdcvgbhnjm', 'awsedftgyhuj']
        self.releases = {
            Release.release: '1',
            Release.cut: '`',
        }

    def send(self, rows):
        time.sleep(0.2)
        keyboard.send('tab')
        keyboard.send('shift+tab')

        def octave_to(new):
            nonlocal octave
            while octave > new:
                octave -= 1
                keyboard.send(self.octave_down)
            while octave < new:
                octave += 1
                keyboard.send(self.octave_up)

        octave = octave0 = None
        for row in rows:
            time.sleep(0.02)
            if isinstance(row, int):
                note = row
                if octave is None:
                    octave = octave0 = note // OCTAVE

                octave_to(note // OCTAVE)
                keyboard.send(self.keyboards[0][note % OCTAVE])

            elif isinstance(row, Release):
                keyboard.send(self.releases[row])
            else:
                keyboard.send('down')

        if octave0 is not None:
            octave_to(octave0)

        # for _ in rows:
        #     keyboard.send('up')
