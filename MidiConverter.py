from midiutil.MidiFile import MIDIFile

volume = 100
off = 21


def set_volume(n):
    return int((n / 2) * volume) if n < 2 else volume


class Midi:
    def __init__(self, tracks=1, tempo=60):
        self.mf = MIDIFile(tracks)
        self.volume = 100
        self.channel = 0
        self.time = time = 0
        self.track = track = 0
        self.mf.addTrackName(track, time, "Sample Track")
        self.mf.addTempo(track, time, 120)
        self.increment = 2 / tempo
        self.duration = self.increment
        self.notes = []
        self.log = []

    def log_end(self):
        for n in self.notes:
            self.mf.addNote(self.track, self.channel, off + n['note'], n['start'], n['duration'],
                            set_volume(n['vol']))
            # self.log[int(n['start'] / self.increment)].append(n.copy())

        # for a in self.log:
        #     for n in a:
        #         self.mf.addNote(self.track, self.channel, off + n['note'], n['start'], n['duration'],
        #                         set_volume(n['vol']))
        #         print((n['note'], n['start'], 4 * n['duration'], set_volume(n['vol'])))

    def log_note(self, pitch):
        for n in self.notes:
            if n['note'] != pitch[0]:
                continue
            if n['duplicate'] == self.time:
                break
            if n['duplicate'] + self.increment >= self.time and n['volume'] >= pitch[1]:
                if n['duration'] > 10:
                    n["duplicate"] = self.time
                    break
                n['duration'] += self.increment
                n['volume'] = pitch[1]
                n["duplicate"] = self.time
                break
            else:
                if n['duration'] > 1/8 and n['vol'] > pitch[1]:
                    self.mf.addNote(self.track, self.channel, off + n['note'], n['start'], n['duration'],
                                    set_volume(n['vol']))
                # self.log[int(n['start'] / self.increment)].append(n.copy())
                n.update({
                    "vol": pitch[1],
                    "volume": pitch[1],
                    "duration": self.increment,
                    "start": self.time,
                    "duplicate": self.time,
                })
                break
        else:
            if pitch[1] < 0.5:
                return
            self.notes.append({
                "note": pitch[0],
                "vol": pitch[1],
                "volume": pitch[1],
                "duration": self.increment,
                "start": self.time,
                "duplicate": self.time,
            })

    def add(self, pitches):
        if pitches != 0:
            self.mf.addNote(self.track, self.channel, off + pitches, self.time, self.duration, self.volume)
        # mf.addNote(track, channel, off + pitches, time, duration, volume)
        self.time += self.increment

    def add_multiple(self, pitches):
        for n in pitches:
            self.mf.addNote(self.track, self.channel, off + n[0], self.time, self.duration, set_volume(n[1]))
        self.time += self.increment

    def log_multiple(self, pitches):
        self.log.append([])
        for n in pitches:
            self.log_note(n)
        self.time += self.increment

    # write it to disk
    def out(self, name="sample.mid"):
        self.log_end()
        with open(name, 'wb') as outf:
            self.mf.writeFile(outf)
        self.mf.close()
