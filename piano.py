from tkinter import ttk

from util import nsew, grid
from midi_convert import convert_track


class Scrollable:
    def __init__(self):
        self.xscrolls = []
        self.yscrolls = []

    def xview(self, *args):
        for scroll in self.xscrolls:
            scroll.xview(*args)

    def yview(self, *args):
        for scroll in self.yscrolls:
            scroll.yview(*args)

    # WHEEL
    def _on_mousewheel(self, event):
        # up down
        for scroll in self.yscrolls:
            scroll.yview_scroll(int(-1 * (event.delta / 120)), 'units')

    def _on_shift_mousewheel(self, event):
        # left right
        for scroll in self.xscrolls:
            scroll.xview_scroll(int(-1 * (event.delta / 120)), 'units')

    # PAGEUP PAGEDOWN
    def _on_pageup(self, event):
        # up
        for scroll in self.yscrolls:
            scroll.yview_scroll(-1, 'pages')

    def _on_pagedown(self, event):
        # down
        for scroll in self.yscrolls:
            scroll.yview_scroll(1, 'pages')

    def _on_shift_pageup(self, event):
        # left
        for scroll in self.xscrolls:
            scroll.xview_scroll(-1, 'pages')

    def _on_shift_pagedown(self, event):
        # right
        for scroll in self.xscrolls:
            scroll.xview_scroll(1, 'pages')

    # HOME END
    def _on_home(self, event):
        # left
        for scroll in self.xscrolls:
            scroll.xview_moveto(0)

    def _on_end(self, event):
        # right
        for scroll in self.xscrolls:
            # WIDTH = x
            visible = scroll.winfo_width()
            total = int(scroll.cget('width'))
            scroll.xview_moveto((total - visible) / total)

    def _on_shift_home(self, event):
        # up
        for scroll in self.yscrolls:
            scroll.yview_moveto(0)

    def _on_shift_end(self, event):
        # down
        for scroll in self.yscrolls:
            # HEIGHT
            visible = scroll.winfo_height()
            total = int(scroll.cget('height'))
            scroll.yview_moveto((total - visible) / total)

    # ARROW KEYS
    def _on_arrow_up(self, event):
        for scroll in self.yscrolls:
            scroll.yview_scroll(-1, 'units')

    def _on_arrow_down(self, event):
        for scroll in self.yscrolls:
            scroll.yview_scroll(1, 'units')

    def _on_arrow_left(self, event):
        for scroll in self.xscrolls:
            scroll.xview_scroll(-1, 'units')

    def _on_arrow_right(self, event):
        for scroll in self.xscrolls:
            scroll.xview_scroll(1, 'units')


# _NOTE_HEIGHT = 16

class PianoPanel(Scrollable):
    COLOR_GRAY = '#CCC'
    COLOR_DARK_GRAY = '#AAA'
    COLOR_PIANO_BLACK = '#F8F0F0'

    def __init__(self, frame, app, initial_tnum, cfg):
        Scrollable.__init__(self)
        self.frame = frame
        self.track_box = None

        self.app = app

        self.note_height = cfg.get('note_height', 16)
        self.qnote_width = cfg.get('qnote_width', 48)
        self.pitch_range = cfg.get('pitch_range', 1200)
        self.vol_expr = cfg.get('vol_expr', lambda v: v)

        self.tickrate = app.tick_rate

        # Dummy out the list box
        # TODO persistent listbox?

        # Convert the track.
        self.tracknum = initial_tnum
        # self.new_tracknum = -1

        self.note_out = None
        self.pitch_out = None
        self.vibrato_out = None
        self.load_track(initial_tnum)


    def load_track(self, track_num):
        # TODO http://effbot.org/tkinterbook/canvas.htm
        # canvas.delete(ALL)  # remove all items

        track = self.app.tracks[track_num]

        note_out, pitch_out, vibrato_out, maxtick = convert_track(track)
        self.note_out = note_out
        self.pitch_out = pitch_out
        self.vibrato_out = vibrato_out

        # Configure the canvas.

        self.maxtick = maxtick
        width = self.calc_x(maxtick)  # Depends on qnote_width
        self.width = width

    def calc_x(self, time):
        # Converts from time to width.
        # Ticks / (ticks/note) * (pixels/note) = pixels
        return round(time * self.qnote_width / self.tickrate + 0.000001)

