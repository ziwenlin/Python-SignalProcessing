import multiprocessing as mp
import threading as th
import serial
import json

import GraphPlotter as plt
# import MidiConverter as em
import SpectrumAnalyse

# init constants
BAUD_RATE = 9600  # serial clock speed

# variables loader
FILEPATH = 'samples/sample.wav'
SERIAL_COM = 'COM4'
INFO = 'Ready'

spa = SpectrumAnalyse.Analyser()

# variables interface
CHUNK = 1024 * 2  # samples per frame
FFT_SPS = 10  # samples per 2 frames
COUNTER = 0
FFT_LENGTH = 0
NEXT = 100
GRAPH = []
DATA = []
MASTER = None
SERIAL_STATE = False
SERIAL_PAUSE = False
START_GRAPH = False
START_STREAM = False
READY = False
READING = False


def json_load():
    global CHUNK, FFT_SPS, NEXT, FILEPATH
    try:
        with open('Settings.json', 'r+') as jsf:
            js = json.load(jsf)
        CHUNK = js["CHUNK"]  # samples per frame
        FFT_SPS = js["FFT_SPS"]  # samples per 2 frames
        NEXT = js["NEXT"]
        FILEPATH = js["FILEPATH"]
    except FileNotFoundError:
        json_save()


def json_save():
    with open('Settings.json', 'w+') as jsf:
        js = json.dumps({
            "CHUNK": CHUNK,
            "NEXT": NEXT,
            "FFT_SPS": FFT_SPS,
            "FILEPATH": FILEPATH,
        })
        jsf.write(js)


def window():
    pass


def streaming():
    while SERIAL_STATE and START_STREAM:
        if SERIAL_STATE and not SERIAL_PAUSE:
            SERIAL.write(bytearray([int(DATA[COUNTER])]))
    stop()
    print("Closing stream")


def stop():
    global SERIAL_STATE
    if SERIAL_STATE is True:
        SERIAL_STATE = False
        print("Closing")
        SERIAL.write(bytearray([0]))
        SERIAL.close()
    else:
        print("Nothing to close")


def read():
    global READY, READING
    if READING:
        print("Already reading")
        return
    READY = False
    READING = True
    json_save()

    def task():
        global spa, READING, READY, INFO, START_GRAPH, START_STREAM, FFT_LENGTH
        spa = SpectrumAnalyse.Analyser(chunk=CHUNK, fft_sps=FFT_SPS)
        spa.start(FILEPATH)
        INFO = "Start FFT"
        spa.calc_fft()
        INFO = "Start RAW MIDI"
        spa.calc_raw_midi()
        INFO = "Start MULTI MIDI"
        spa.calc_multi_midi()
        INFO = "Start: SINGLE MIDI"
        spa.calc_single_midi()
        INFO = "Start: SMART MIDI"
        spa.calc_pitches()
        INFO = "Length:%s Samplerate:%s" % (spa.fft.length, spa.RATE)
        FFT_LENGTH = spa.fft.length - 1
        print("Reading completed")
        START_STREAM = False
        START_GRAPH = False
        READY = True
        READING = False

    print("Start Reading")
    th.Thread(target=task, daemon=True).start()


def start():
    global SERIAL, DATA, NEXT, SERIAL_STATE, SERIAL_PAUSE, START_STREAM
    if READY and not SERIAL_STATE:
        try:
            SERIAL = serial.Serial(SERIAL_COM, baudrate=BAUD_RATE)
            th.Thread(target=streaming, daemon=True).start()
            print(SERIAL)
            DATA = spa.raw_midi.data.tolist()
            START_STREAM = True
            SERIAL_STATE = True
            SERIAL_PAUSE = False
        except:
            print("No Serial Connected")
    else:
        print('Not ready')


def pause():
    global SERIAL_PAUSE, COUNTER
    if not SERIAL_STATE:
        print("Not started yet")
        return
    SERIAL_PAUSE = not SERIAL_PAUSE
    print("PAUSED" if SERIAL_PAUSE else "CONTINUE")


def clear():
    global SERIAL, SERIAL_STATE
    try:
        if SERIAL_STATE is False:
            SERIAL = serial.Serial(SERIAL_COM)
            SERIAL.close()
        else:
            SERIAL_STATE = False
            SERIAL.close()
            SERIAL = serial.Serial(SERIAL_COM)
            SERIAL.close()
    except:
        print("No Serial Connected")


def plt_create(x_data=None, y_lim=(-1, 1), x_scale='linear'):
    def plt_task():
        global GRAPH, graph, START_GRAPH
        try:
            if x_data is not None:
                graph = plt.Graph(x_data, GRAPH[0])
            else:
                graph = plt.Graph(GRAPH[0])
            graph.ax.set_ylim(y_lim)
            graph.ax.set_xscale(x_scale)
            graph.start(window())
            START_GRAPH = True
            th.Thread(target=plt_graph, daemon=True).start()
        except IndexError:
            print("No data available")

    global START_GRAPH
    START_GRAPH = False
    MASTER.after(100, plt_task)


def plt_audio():
    global GRAPH
    GRAPH = [spa.audio.next_data() for _ in range(spa.fft.length)]
    plt_create()


def plt_freq():
    global GRAPH, graph
    GRAPH = spa.pitches.data
    plt_create(spa.pitches.x, (0, 5), 'log')


def plt_fft():
    global GRAPH, graph
    GRAPH = spa.fft.data
    plt_create(spa.fft.x, (0, 5), 'log')


def plt_graph():
    def draw():
        global GRAPH
        if not START_GRAPH:
            graph.close()
            return
        graph.draw()
        graph.update(GRAPH[COUNTER])
        graph.master.after(50, draw)

    graph.master.after(100, draw)


def plt_close():
    global START_GRAPH
    START_GRAPH = False


def convert(data=None, txt='', note=0, fp='', tempo=10):
    # print("Start %s midi" % (fp, ))
    if data is None:
        data = []
    track = em.Midi(tempo=tempo, )
    if note == 1:
        for i in data:
            track.log_multiple(i)
    else:
        for i in data:
            track.add_multiple(i)
    path = fp.split('.')[0] + txt + '.mid'
    track.out(path)
    del track
    print("Done %s midi" % path)


def midi():
    if not READY:
        return

    def midi_task():
        mid = [[(m, 40)] if m else [] for m in spa.single_midi.data.tolist()]
        pit = spa.multi_midi.data.tolist()
        raw = spa.raw_midi.data.tolist()
        sma = [[(m, n*2) for m, n in enumerate(j)] for j in spa.pitches.data]
        for n in (
                [sma, 'xm', 0],
                [mid, 'sm', 0],
                [raw, 'rm', 0],
                [pit, 'fm', 0],
                [mid, 'sml', 1],
                [raw, 'rml', 1],
                [pit, 'fml', 1],
                [sma, 'xml', 1],
        ):
            n += [FILEPATH, spa.FFT_SPS]
            mp.Process(target=convert, args=n).start()

    th.Thread(target=midi_task).start()
