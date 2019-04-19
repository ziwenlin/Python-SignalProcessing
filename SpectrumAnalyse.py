import soundfile as sf
import numpy as np
import scipy.signal

import ArduinoPitches as Ap
import multiprocessing as mp

MAX_SIZE_FFT = 1024 * 4


def pool_fft(data, chunk_h):
    real_fft_data = np.fft.rfft(data)[:MAX_SIZE_FFT]
    fft = np.abs(real_fft_data) * (64 / chunk_h)
    return fft  # [data if data > 0.2 else 0 for data in fft_data]


def pool_multi_midi(pitches_s):
    highest = max([i[1] for i in pitches_s[:5]]) if len(pitches_s) > 0 else 0
    pitches_b = [peak if (peak[1] / highest) > 0.1 else None for peak in pitches_s[:5]] if highest > 0 else []
    while None in pitches_b:
        pitches_b.remove(None)
    return pitches_b


def pool_raw_midi(data, x):
    # peaks_n = scipy.signal.find_peaks(fft, threshold=0.8, height=0.5)
    peaks_n = scipy.signal.find_peaks(data, threshold=0.2)
    pitches = [(Ap.pitch(x[n]), data[n]) for n in peaks_n[0]]
    pitches_s = sorted(pitches, key=lambda x: x[1], reverse=True)
    return pitches_s


def pool_single_midi(data, x):
    max_fft = max(data)
    peak_n = np.argmax(data)
    peak_x = x[peak_n]
    pitch = Ap.pitch(peak_x)
    if max_fft < 1:
        pitch = 0
    return pitch


def pool_pitches(data, x):
    midi = [0 for _ in range(len(Ap.pitches))]
    for i, j in zip(data, x):
        if midi[j] > i:
            continue
        midi[j] = i
    return midi


class Arrays:
    def __init__(self, data=np.array([]), increment=1):
        self.length = len(data)
        self.status = 0
        self.start = 0
        self.step = increment
        self.increment = increment
        self.temp = []
        self.x = np.array([])
        self.data = data

    def convert(self):
        self.set_data(np.array(self.temp))
        self.temp.clear()

    def set_data(self, data):
        self.data = data
        self.length = len(data)

    def next_status(self):
        self.status = int(100 * self.step / self.length)
        return self.status

    def next_data(self):
        if self.step >= self.length:
            self.step -= self.start
            self.start = 0
        data: np.ndarray = self.data[self.start:self.step]
        self.start += self.increment
        self.step += self.increment
        return data


class Analyser:
    def __init__(self, chunk=1024 * 2, fft_sps=10):
        # constants
        self.CHUNK = chunk  # samples per frame
        self.CHUNK_H = int(self.CHUNK / 2)
        self.RATE = 44100  # samples per second
        self.FFT_SPS = fft_sps  # fft samples per second

        self.audio = Arrays()
        self.fft = Arrays()
        self.pitches = Arrays()
        self.single_midi = Arrays()
        self.multi_midi = Arrays()
        self.raw_midi = Arrays()

    def start(self, path):
        self.audio.data, self.RATE = sf.read(path)
        if type(self.audio.data[0]) != np.float64:  # check if multi-channel
            self.audio.data = np.split(self.audio.data, len(self.audio.data[0]), axis=1)[0]  # drop second array
            self.audio.data = np.array([i[0] for i in self.audio.data])  # make pretty array
        self.audio.length = len(self.audio.data)
        self.audio.increment = int(self.RATE / self.FFT_SPS)
        self.audio.step = self.CHUNK
        return self.audio.data

    def calc_fft(self):
        self.fft.x = np.linspace(0, self.RATE, self.CHUNK)[:MAX_SIZE_FFT]
        audio = []
        while self.audio.next_status() < 100:
            audio.append((self.audio.next_data(), self.CHUNK_H))
        pool = mp.Pool(mp.cpu_count())
        self.fft.temp = pool.starmap(pool_fft, audio)
        self.fft.convert()
        pool.close()

    def calc_pitches(self):
        self.pitches.x = Ap.pitches
        x = [Ap.pitch(i) for i in self.fft.x]
        fft = [(y, x) for y in self.fft.data]
        pool = mp.Pool(mp.cpu_count())
        self.pitches.temp = pool.starmap(pool_pitches, fft)
        self.pitches.convert()
        pool.close()

    def calc_raw_midi(self):
        fft = [(y, self.fft.x) for y in self.fft.data]
        pool = mp.Pool(mp.cpu_count())
        self.raw_midi.temp = pool.starmap(pool_raw_midi, fft)
        self.raw_midi.convert()
        pool.close()

    def calc_multi_midi(self):
        pitches = self.raw_midi.data
        pool = mp.Pool(mp.cpu_count())
        self.multi_midi.temp = pool.map(pool_multi_midi, pitches)
        self.multi_midi.convert()
        pool.close()

    def calc_single_midi(self):
        fft = [(data, self.fft.x) for data in self.fft.data]
        pool = mp.Pool(mp.cpu_count())
        self.single_midi.temp = pool.starmap(pool_single_midi, fft)
        self.single_midi.convert()
        pool.close()

