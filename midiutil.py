from midi import MIDI as _MIDI


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


# def insert_keyed(in_list, val, key):
#     # Locate the leftmost value >= x
#     for idx, element in enumerate(in_list):
#         if key(element) >= key(val):
#             in_list.insert(idx, val)
#             return
#
#     in_list.append(val)
#
#
# def insert_keyed_after(in_list, val, key):
#     # Locate the rightmost value <= x
#     for idx, element in reversed(enumerate(in_list)):
#         if key(element) <= key(val):
#             in_list.insert(idx + 1, val)
#             return
#
#     in_list.insert(0, val)
