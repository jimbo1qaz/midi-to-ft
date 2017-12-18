from midi import MIDI as _MIDI
from util import dict_find, dict_loose


def event_is_vol(event):
    return event[0] == 'control_change' and event[3] == 0x07


def event_is_pan(event):
    return event[0] == 'control_change' and event[3] == 0x0A


def get_channel(track):
    channel = -1
    for event in track:
        command = event[0]
        if command in _MIDI.Event2channelindex:
            channel = event[_MIDI.Event2channelindex[command]]
            break
    return channel


# TODO: vgmtrans produces multipley-named track 0.
def get_name(track):
    # ['track_name', time, text]
    name = 'Unnamed Track'
    for event in track:
        command = event[0]
        if command == 'track_name':
            name = event[2]
            break
    return name


def get_instrs(track):
    return {event[3] for event in track if event[0] == 'patch_change'}


PITCH_INDEX = {'note': 4, 'key_after_touch': 3}
VELOCITY_INDEX = {'note': 5, 'key_after_touch': 4, 'channel_after_touch': 3}

# See fix_zero.txt.
TRACK_0_KEEP = [
    'copyright_text_event',
    'set_tempo',
    'time_signature',
    'key_signature',
    'marker',
    'smpte_offset'
    # TODO: set_sequence_number could appear anywhere, don't shove it in track 0.
]

def sort_track(track):
    track.sort(key=lambda event: event[1])


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

def note2sci(note):
    note2letter = ['C', 'C#', 'D', 'D#', 'E', 'F',
                   'F#', 'G', 'G#', 'A', 'A#', 'B']
    octave = note // 12 - 1
    letter = note2letter[note % 12]
    return letter + str(octave)
