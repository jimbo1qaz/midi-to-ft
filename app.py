import sys
from tkinter import *
from tkinter.scrolledtext import ScrolledText
from tkinter import ttk

from midi import MIDI
import midiutil

from piano import PianoPanel
from util import zeros, nsew, grid, weigh, y_weigh

ROOT = Tk()


# def get_root():
#     return ROOT


"""
root
layout
    0,0: piano frame
    0,1: command frame
    ctrl+s = save file
"""


INITIAL_TNUM = 0



def wtf(frame):
    def key(event):
        print("pressed", repr(event.char))

    def callback(event):
        frame = event.widget
        frame.focus_set()
        print("clicked at", event.x, event.y)

    frame.bind("<Key>", key)
    frame.bind("<Button-1>", callback)



class App:
    def __init__(self, filename, cfg: dict):
        self.cfg = cfg

        # **** MIDI setup ****
        with open(filename, 'rb') as file:
            score = MIDI.midi2score(file.read())

        self.tick_rate = score[0]
        self.tracks = score[1:]
        self.track_names = track_names_uh(self.tracks)

        # **** GUI setup ****

        self.root = root = ROOT
        root.title('midi2fami')
        root.geometry("640x800")
        weigh(root)

        # root.
        self.layout = layout = ttk.Frame(root, padding=zeros)
        grid(layout, sticky=nsew)
        y_weigh(layout, [1, 0])

        # root.layout.
        piano_frame = ttk.Frame(layout, width=640, height=480)
        grid(piano_frame, 0, 0, sticky=nsew)
        self.piano = PianoPanel(piano_frame, self, INITIAL_TNUM, cfg)   # fixme
        # wtf(piano_frame)

        script_frame = ttk.Frame(layout)
        grid(script_frame, 0, 1, sticky=nsew)
        self.script = ScriptPanel(script_frame, cfg)


def track_names_uh(tracks):
    track_names = []
    track_instrs = []

    # Loop through all specified tracks.

    for i, track in enumerate(tracks):
        track_names.append(midiutil.get_name(track)
                           .encode('latin-1')
                           .decode('ascii', 'backslashreplace'))

        is_perc = (midiutil.get_channel(track) == 9)
        used_insts = midiutil.get_instrs(track)
        inst_list = sorted([midiutil.instr_fmt(x, is_perc) for x in used_insts])

        instr_text = ', '.join(inst_list)

        track_instrs.append(instr_text)

    name_max = max(len(name) for name in track_names)

    ret = []
    for i in range(len(tracks)):
        ret.append(str(i).ljust(4) + '| ' + track_names[i].ljust(name_max + 4) + '| ' + track_instrs[i])
    return ret


class ScriptPanel:
    def __init__(self, frame, cfg):
        assert cfg or True
        self.frame = frame
        weigh(frame)

        fill = ScrolledText(frame, height=16)
        grid(fill, sticky=nsew)


path = r'C:\Users\jimbo1qaz\Dropbox\encrypted\projects\eirin\th08_14-modified.mid'
# sys.argv.append(r'C:\Users\jimbo1qaz\Dropbox\encrypted\projects\eirin\th08_14-modified.mid')
f = App(path, {})
f.root.mainloop()

# ROOT.mainloop()
