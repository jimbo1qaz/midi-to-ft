from tkinter import *

root = Tk()


def wtf(frame):
    def key(event):
        print("pressed", repr(event.char))

    def callback(event):
        frame.focus_set()
        print("clicked at", event.x, event.y)

    frame.bind("<Key>", key)
    frame.bind("<Button-1>", callback)


frame = Frame(root, width=100, height=100)
wtf(frame)
frame.pack()

root.mainloop()
