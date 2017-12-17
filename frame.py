from tkinter import *
from tkinter import ttk

# FONT = '"Small Fonts" 8'
FONT = '"DejaVu Sans Mono" 9'

zeros = (0, 0, 0, 0)
nsew = 'nsew'


def xy(x, y):
    return {'column': x, 'row': y}


def grid(widget: Widget, x=0, y=0, **kwargs):
    widget.grid(column=x, row=y, **kwargs)


def y_expand(frame: ttk.Frame, rows, **kw_rows):
    for row, weight in enumerate(rows):
        frame.rowconfigure(row, weight=weight)
    for row, weight in kw_rows.items():
        frame.rowconfigure(row, weight=weight)


ROOT = Tk()


def get_root():
    return ROOT


"""
root
layout
    0,0: piano frame
    0,1: command frame
    ctrl+s = save file
"""


class App:
    def __init__(self, cfg):
        self.cfg = cfg

        self.root = root = ROOT
        root.title('midi2fami')
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)

        # root.
        self.layout = layout = ttk.Frame(root, padding=zeros)
        grid(layout, sticky=nsew)
        y_expand(layout, [2, 1])

        # root.layout.
        piano_frame = ttk.Frame(layout)#, padding=zeros
        grid(piano_frame, 0, 0, sticky=nsew)
        self.piano = PianoPanel(piano_frame, cfg)

        script_frame = ttk.Frame(layout)#, padding=zeros
        grid(script_frame, 0, 1, sticky=nsew)
        self.script = ScriptPanel(script_frame, cfg)


class PianoPanel:
    def __init__(self, frame, cfg):
        self.frame = frame

        fill = ttk.Label(frame, text="Piano")
        grid(fill, sticky=nsew)


class ScriptPanel:
    def __init__(self, frame, cfg):
        self.frame = frame

        fill = Text(frame, height=8)
        grid(fill, sticky=nsew)


f = App(None)
f.root.mainloop()
