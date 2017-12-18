from tkinter import *
from tkinter import ttk

from midi_convert import convert_track
from midiutil import note2sci
from util import nsew, grid, FONT, I, recursive_bind


# class DebugScrollbar(ttk.Scrollbar):
#     def set(self, *args):
#         print("SCROLLBAR SET", args)
#         Scrollbar.set(self, *args)


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
            scroll.yview_scroll(int(-1 * (event.delta / 60)), 'units')

    def _on_shift_mousewheel(self, event):
        # left right
        for scroll in self.xscrolls:
            scroll.xview_scroll(int(-1 * (event.delta / 60)), 'units')

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

    #

    @staticmethod
    def _onclick(event: Event):
        print(event)
        event.widget.focus_set()

    # *************************************
    # **** Scrollable drawing commands ****
    # *************************************

    def draw_vline(self, x, **kwargs):
        for canvas in self.xscrolls:
            height_str = canvas.cget('height')
            height = int(height_str)
            canvas.create_line(x, 0, x, height, **kwargs)

    @staticmethod
    def draw_single_vline(canvas, x, **kwargs):
        height_str = canvas.cget('height')
        height = int(height_str)
        canvas.create_line(x, 0, x, height, **kwargs)

    #

    def draw_hline(self, y, **kwargs):
        for canvas in self.yscrolls:
            # Drawing a horizontal line, you must calculate the width of the canvas.
            width_str = canvas.cget('width')
            width = int(width_str)
            canvas.create_line(0, y, width, y, **kwargs)

    @staticmethod
    def draw_single_hline(canvas, y, **kwargs):
        # Drawing a horizontal line, you must calculate the width of the canvas.
        width_str = canvas.cget('width')
        width = int(width_str)
        canvas.create_line(0, y, width, y, **kwargs)

    #

    @staticmethod
    def draw_text(canvas, x, y, text, **kwargs):
        canvas.create_text(x, y, anchor='w', font=FONT, text=text, **kwargs)


# _NOTE_HEIGHT = self.note_height

PADDING = 1

class PianoPanel(Scrollable):
    COLOR_GRAY = '#CCC'
    COLOR_DARK_GRAY = '#AAA'
    COLOR_PIANO_BLACK = '#F8F0F0'

    MIDI_NOTES = 128
    MIDI_VOLUME = 128

    def calc_x(self, time):
        # Converts from time to width.
        # Ticks / (ticks/note) * (pixels/note) = pixels
        return round(time * self.qnote_width / self.tickrate + 0.000001)

    def calc_y(self, note):
        return self.note_height * (self.MIDI_NOTES - note - 1)

    def pitch_calc_y(self, cents):
        pitch_height = int(self.pitch_canvas.cget('height'))
        pixel_range = pitch_height // 2
        # Scales pitch_range to pixel_range
        scaled_cents = cents * pixel_range // self.pitch_range

        # Because positive pitch is negative pixels
        return pixel_range - scaled_cents



    def __init__(self, frame, app, initial_tnum, cfg):

        # **** FRAMEWORK SETUP ****

        Scrollable.__init__(self)
        self.frame = frame

        self.track_box = None

        self.app = app

        # **** MIDI to GUI ****

        self.note_height = cfg.get('note_height', 16)
        self.qnote_width = cfg.get('qnote_width', 48)
        self.pitch_range = cfg.get('pitch_range', 1200)
        self.vol_expr = cfg.get('vol_expr', lambda v: v)

        self.tickrate = app.tick_rate

        self.width = None


        # **** SETUP CANVASes ****

        frame.columnconfigure(1, weight=1)
        frame.rowconfigure(2, weight=1)

        frame.columnconfigure(1, weight=1)
        frame.rowconfigure(2, weight=1)

        self.canvases = []

        # Primary canvas
        canvas = self.create_canvas(0, self.note_height * self.MIDI_NOTES)
        self.canvas = canvas
        canvas.grid(column=1, row=2, sticky=nsew, padx=PADDING, pady=PADDING)
        self.xscrolls.append(canvas)
        self.yscrolls.append(canvas)

        # Note labels
        labels = self.create_canvas(64, self.note_height * self.MIDI_NOTES)
        self.labels = labels
        labels.grid(column=0, row=2, sticky=nsew, padx=PADDING, pady=PADDING)
        self.yscrolls.append(labels)

        # Time canvas
        time_canvas = self.create_canvas(0, self.note_height)
        self.time_canvas = time_canvas
        time_canvas.grid(column=1, row=1, sticky=nsew, padx=PADDING, pady=PADDING)
        self.xscrolls.append(time_canvas)

        # Pitch canvas
        pitch_canvas = self.create_canvas(0, 0*self.MIDI_NOTES)
        self.pitch_canvas = pitch_canvas
        pitch_canvas.grid(column=1, row=3, sticky=nsew, padx=PADDING, pady=PADDING)
        self.xscrolls.append(pitch_canvas)

        # Vibrato canvas
        vibrato_canvas = self.create_canvas(0, 0*32)
        self.vibrato_canvas = vibrato_canvas
        vibrato_canvas.grid(column=1, row=4, sticky=nsew, padx=PADDING, pady=PADDING)
        self.xscrolls.append(vibrato_canvas)

        self.tracknum = initial_tnum

        self.setup_toolbar(app.track_names, initial_tnum)
        self.setup_scrolls()

        self.load_track(initial_tnum)


    def load_track(self, track_num):
        """ Load track, (re)initialize canvases. """
        track = self.app.tracks[track_num]

        note_out, pitch_out, vibrato_out, maxtick = convert_track(track)
        self.note_out = note_out
        self.pitch_out = pitch_out
        self.vibrato_out = vibrato_out

        # Configure the canvas.

        self.maxtick = maxtick
        width = self.calc_x(maxtick)  # Depends on qnote_width
        self.width = width

        # we could add method to recreate all canvases.

        for canvas in self.canvases:    # type: Canvas
            canvas.delete(ALL)

        for canvas in self.xscrolls:    # type: Canvas
            canvas.configure(width=self.width)

            scroll = I(canvas['scrollregion'])  # x0 y0 x1 y1
            scroll[2] = width
            canvas.configure(scrollregion=scroll)


        self.setup_background()
        self.setup_measures()
        self.draw()




    # UTILITY
    def create_canvas(self, width, height):
        canvas = Canvas(self.frame, bg='#FFF', scrollregion=(0, 0, width, height),
                        width=width, height=height, bd=0, highlightthickness=0, relief='ridge',
                        takefocus=True)     # FIXME clickable focus?
        self.canvases.append(canvas)
        return canvas

    def setup_toolbar(self, track_list, tnum):
        toolbar = ttk.Frame(self.frame)
        # toolbar.configure(padding=1)
        grid(toolbar, 0, 0, sticky=(N, S, E, W), columnspan=3)

        self.track_box = track_box = ttk.Combobox(
            toolbar, values=track_list,
            height=1000, width=50, state='readonly'
        )
        grid(track_box, 0, 0)

        track_box.current(tnum)

        # Bind events to select next track.
        track_box.bind('<<ComboboxSelected>>', self._on_list_selected)
        pass

    def _on_list_selected(self, event):
        self.tracknum = self.track_box.current()
        self.load_track(self.tracknum)
        self.frame.focus_set()

    def setup_scrolls(self):
        root = self.frame   # fixme
        # Vertical scrollbar
        self.vbar = vbar = ttk.Scrollbar(self.frame, orient=VERTICAL, command=self.yview)
        vbar.grid(column=2, row=2, sticky=(N, W, E, S))
        self.canvas.configure(yscrollcommand=vbar.set)

        # Horizontal scrollbar
        self.hbar = hbar = ttk.Scrollbar(self.frame, orient=HORIZONTAL, command=self.xview)
        hbar.grid(column=1, row=100, sticky=(N, W, E, S))
        self.canvas.configure(xscrollcommand=hbar.set)

        # Not scrollbars, but the best place to put them.
        recursive_bind(root, '<Shift-MouseWheel>', self._on_shift_mousewheel)
        recursive_bind(root, '<MouseWheel>', self._on_mousewheel)
        recursive_bind(root, '<Button-4>', self._on_mousewheel)
        recursive_bind(root, '<Button-5>', self._on_mousewheel)

        recursive_bind(root, '<Prior>', self._on_pageup)
        recursive_bind(root, '<Next>', self._on_pagedown)
        recursive_bind(root, '<Shift-Prior>', self._on_shift_pageup)
        recursive_bind(root, '<Shift-Next>', self._on_shift_pagedown)

        recursive_bind(root, '<Home>', self._on_home)
        recursive_bind(root, '<End>', self._on_end)
        recursive_bind(root, '<Shift-Home>', self._on_shift_home)
        recursive_bind(root, '<Shift-End>', self._on_shift_end)

        recursive_bind(root, '<Up>', self._on_arrow_up)
        recursive_bind(root, '<Down>', self._on_arrow_down)
        recursive_bind(root, '<Left>', self._on_arrow_left)
        recursive_bind(root, '<Right>', self._on_arrow_right)

        recursive_bind(root, '<Button-1>', self._onclick)


    def setup_background(self):
        canvas = self.canvas
        pitch_canvas = self.pitch_canvas
        width = self.width

        # Draw note lines
        for note in range(128):
            if note % 12 in [1,3,6,8,10]:
                y = self.calc_y(note)
                canvas.create_rectangle(0, y, width, y+self.note_height, width=0, fill=self.COLOR_PIANO_BLACK)
        for note in range(128):
            y = self.calc_y(note)
            self.draw_hline(y)
            if note % 12 == 0:
                self.draw_hline(y + 15)

        # Draw note labels
        # (optional) percussion names?
        for y in range(128):
            self.labels.create_text(29, self.calc_y(y) + 8, anchor='e', font=FONT,
                                    text=str(y))
            self.labels.create_text(62, self.calc_y(y) + 8, anchor='e', font=FONT,
                                    text=note2sci(y))

        # TODO one object per canvas
        # Draw the pitch canvas lines
        # Zero marking
        self.draw_single_hline(pitch_canvas, self.pitch_calc_y(0), width=3)

        for y in range(100, self.pitch_range, 100):
            upper = self.pitch_calc_y(y)
            lower = self.pitch_calc_y(-y)

            # Even markings are darker
            if y // 100 % 2 == 0:
                color = '#000'
            else:
                color = self.COLOR_GRAY
            self.draw_single_hline(pitch_canvas, upper, fill=color)
            self.draw_single_hline(pitch_canvas, lower, fill=color)

        # draw dividing line
        self.draw_single_vline(self.labels, 31)

    # TODO: config object
    def setup_measures(self):
        # The multiplier converts ticks to pixels.
        tickrate = self.tickrate
        maxtick = self.maxtick

        # draw measure lines
        for measure_tick in range(0, maxtick, 4 * tickrate):  # fsck me right? Always assuming 4:4 songs... RIGHT?
            # Convert the measure tick into pixels, then draw the line.
            measure_num = measure_tick // (4 * tickrate)
            measure_x = self.calc_x(measure_tick)
            measure_x -= 1  # Create a double-thickness line. Not for the first, though.
            # Doesn't really matter, but inconsistent.
            self.draw_text(self.time_canvas, measure_x + 4, 8, str(measure_num))
            self.draw_vline(measure_x)

        # Draw note lines
        for note_tick in range(0, maxtick, tickrate):
            note_x = self.calc_x(note_tick)
            self.draw_vline(note_x)

        # Draw self.note_heightth notes (quarter note * divide_factor=4) = self.note_height
        divide_factor = 4
        # There are maxtick ticks.
        # Each increment advances (tickrate/divide_factor) ticks.
        # There are maxtick/(increment_size) increments total.
        increment_size = tickrate / divide_factor
        for i in range(int(maxtick / increment_size)):
            if i % 4 == 0:
                continue
            time = tickrate * i // divide_factor
            x = self.calc_x(time)
            self.draw_vline(x, fill=self.COLOR_GRAY)

    def draw(self):
        canvas = self.canvas
        pitch_canvas = self.pitch_canvas

        # draw notes
        for pitch, pitch_dict in enumerate(self.note_out):
            for time, note_tuple in pitch_dict.items():
                note_pitch = note_tuple[0]
                # volume = round((note_tuple[1] / 79) ** 2 * 99)
                # volume = note_tuple[1] * 2
                volume = self.vol_expr(note_tuple[1])

                end_time = note_tuple[2]
                if pitch != note_pitch:
                    print('ERROR INCORRECT PITCH IN NOTE!')
                    print(pitch)
                    print(note_pitch)
                    raise Exception
                # Calculate the note's position, and draw it.
                note_x = self.calc_x(time)
                note_y = self.calc_y(pitch)
                note_end = self.calc_x(end_time)

                # Fill color is blue for note extensions
                if volume < 0:
                    fill = '#BBF'
                else:
                    fill = '#FBB'

                volume = abs(volume)

                amount_filled = volume / self.MIDI_VOLUME * self.note_height

                canvas.create_rectangle(note_x, note_y,
                                        note_end, note_y + self.note_height, fill=self.COLOR_GRAY)
                canvas.create_rectangle(note_x, note_y + self.note_height - amount_filled,
                                        note_end, note_y + self.note_height, fill=fill)
                self.draw_text(canvas, note_x + 2, note_y - 4, str(abs(volume)))
                # DEBUGGING
                # self.draw_text(canvas, note_x + 32, note_y + 8, str(time))
                # self.draw_text(canvas, note_x + 64, note_y + 8, str(end_time))

        # Draw pitch bends.
        prev_x = 0
        prev_y = 32
        for time, pitch in sorted(self.pitch_out.items()):
            curr_x = self.calc_x(time)
            curr_y = self.pitch_calc_y(pitch)

            # Draw previous crossbar.
            pitch_canvas.create_line(prev_x, prev_y, curr_x, prev_y, width=3, fill='#F00')
            # Draw previous vertical bar.
            pitch_canvas.create_line(curr_x, prev_y, curr_x, curr_y, fill='#F00')

            # Remove text for clarity.
            # self.draw_text(pitch_canvas, curr_x + 2, curr_y, str(pitch))
            prev_x = curr_x
            prev_y = curr_y
