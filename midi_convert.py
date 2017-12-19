import inspect


# event, ... , channel, params...
from util import epsilon

PITCH_EVENTS = ['note', 'key_after_touch']
DEBUGON = ['convert_track']


def PRINT(*args, **kwargs):
    if inspect.stack()[1][3] in DEBUGON:
        print(*args, **kwargs)


def vol_combine(a, b):
    return round((a / 127) * (b / 127) * 127 + epsilon)


def remove_end_notes(currnotes, time):
    """Removes notes which have ended. In-place."""
    pass # PRINT(currnotes)
    pass # PRINT('Removing until', time)
    for pitch, note in enumerate(currnotes):
        if note is not None and time >= note[3]:
            pass # PRINT('Removing', note[3])
            currnotes[pitch] = None
    pass # PRINT(currnotes)
    # if currnotes == [None] * 128:
    #     pass # PRINT('Nothing')
    #     pass

    pass # PRINT()


def pitch2cents(pitch, cent_range):
    # Originally 14 bits, subtract 0x2000 is 13 bits plus sign = 0x2000 range.
    return int(cent_range * pitch / 0x2000)


def convert_track(track):
    track = sorted(track, key=lambda event: event[1])   # Sort by time (much profanity was spent on this)
    maxtick = 0
    note_out = []   # Pitch -> Time -> [Pitch, Volume, Endtime]
    pitch_raw = {}
    pitch_out = {}  # Time -> Cents
    vibrato_out = {}    # Time -> Units (cents?)

    for x in range(128):
        note_out.append({})

    currvol = 127
    pitch_range_notes = 0
    pitch_range_cents = 0
    pitch_range = 0     # In cents

    currnotes = [None] * 128    # Pitch -> [Pitch, Volume, Time, Endtime, Velocity]

    rpn_msb = rpn_lsb = 0

    for event in track:
        if event[0] == 'note':
            time = event[1]
            dur = event[2]
            pitch = event[4]
            vel = event[5]
            maxtick = max(maxtick, time + dur)    # end of note, non-inclusive

            endtime = time + dur

            # Add the event to the list
            note_out[pitch][time] = [pitch, vol_combine(currvol, vel), endtime]
            currnotes[pitch] = [pitch, vol_combine(currvol, vel), time, endtime, vel]
            pass # PRINT('Adding note', time)
            remove_end_notes(currnotes, time)

        elif event[0] == 'control_change':
            # ['control_change', dtime, channel, controller(0-127), value(0-127)]
            type = event[3]
            time = event[1]
            maxtick = max(maxtick, time)

            # Volume change
            if type == 0x07:
                pass # PRINT('Vol-event Time:', time)
                vol = event[4]
                currvol = vol

                pass # PRINT('Volume:', vol)
                # Remove notes which have ended, so you don't push extra renote events.
                remove_end_notes(currnotes, time)

                for note in currnotes:
                    if note is None:
                        continue
                    pitch = note[0]
                    orig_start = note[2]
                    endtime = note[3]
                    velocity = note[4]

                    pass # PRINT('MIDI_CONVERT Volifying note', pitch, orig_start)

                    new_combine = vol_combine(currvol, velocity)
                    if time not in note_out[pitch]:
                        new_combine *= -1    # Extensions of existing notes are negated
                                        # in order to distinguish from new notes.

                    # Original note = before.
                    note_out[pitch][orig_start][2] = time   # Truncate the end time.
                    # New note = after. (New)
                    note_out[pitch][time] = [pitch, new_combine, endtime]
                    # Current note = after.
                    currnotes[pitch][2] = time
                    # Pitch bends are control changes with RPN 0x0000, MSB = semitones, LSB = cents

            # Modulation Vibrato change
            elif type == 0x01:
                vibrato_out[time] = event[4]

            # Registered Parameter Numbers (Pitch Range)
            elif type == 0x65:  # 0x65 RPN MSB
                rpn_msb = event[4]
            elif type == 0x64:  # 0x64 RPN LSB
                rpn_lsb = event[4]
            elif type == 0x06:  # 0x06 MSB
                if rpn_msb == 0x00:     # Curr RPN = Pitch bend
                    pitch_range_notes = event[4]
                    pitch_range = 100 * pitch_range_notes + pitch_range_cents
                    if time in pitch_raw:
                        pitch_out[time] = pitch2cents(pitch_raw[time], pitch_range)
            elif type == 0x26:  # 0x26 LSB
                if rpn_msb == 0x00:     # Curr RPN = Pitch bend
                    pitch_range_cents = event[4]
                    pitch_range = 100 * pitch_range_notes + pitch_range_cents
                    if time in pitch_raw:
                        pitch_out[time] = pitch2cents(pitch_raw[time], pitch_range)

        elif event[0] == 'pitch_wheel_change':
            time = event[1]
            value = event[3]
            maxtick = max(maxtick, time)

            pitch_raw[time] = value
            pitch_out[time] = pitch2cents(value, pitch_range)

    return note_out, pitch_out, vibrato_out, maxtick
