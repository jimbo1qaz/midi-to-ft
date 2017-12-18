from tkinter import *
from tkinter import ttk

from midi import MIDI
import midiutil

from piano import PianoPanel
from script2ft import ScriptPanel
from util import weigh

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
        self.layout = layout = ttk.PanedWindow(root)
        layout.pack(fill=BOTH, expand=1)

        # root.layout.
        piano_frame = ttk.Frame(layout, width=640, height=480)
        layout.add(piano_frame, weight=1)
        self.piano = PianoPanel(piano_frame, self, INITIAL_TNUM, cfg)   # fixme

        script_frame = ttk.Frame(layout)
        layout.add(script_frame)
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


path = r'C:\Users\jimbo1qaz\Dropbox\encrypted\projects\eirin\th08_14-modified.mid'
# sys.argv.append(r'C:\Users\jimbo1qaz\Dropbox\encrypted\projects\eirin\th08_14-modified.mid')
f = App(path, {})
f.root.mainloop()

# ROOT.mainloop()
