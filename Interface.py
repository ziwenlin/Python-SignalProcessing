import Program as Pg

if __name__ == '__main__':
    import tkinter as tk

    Pg.json_load()

    window = tk.Tk("Serial Speaker")
    window.minsize(800, 200)
    Pg.MASTER = window
    Pg.window = tk.Toplevel

    frame_reader = tk.Frame(window, padx=3, pady=5, width=200, bg='darkgrey')
    frame_reader.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    frame_serial = tk.Frame(window, padx=3, pady=5, width=200, bg='darkgrey')
    frame_serial.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    frame = tk.Frame(window, padx=3, pady=5, width=200, bg='darkgrey')
    frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    # READER
    button_midi = tk.Button(frame_reader, text='Convert to Midi', command=Pg.midi)
    button_read = tk.Button(frame_reader, text='Read file', command=Pg.read)
    entry_chunk = tk.Scale(frame_reader, from_=1, to=128, resolution=1, orient=tk.HORIZONTAL)
    entry_speed = tk.Scale(frame_reader, from_=4, to=200, orient=tk.HORIZONTAL)
    entry_path = tk.Entry(frame_reader)
    label_speed = tk.Label(frame_reader, text='FFT Samples per seconds', height=2, bg='lightgrey')
    label_chunk = tk.Label(frame_reader, text='Chunk size', height=2, bg='lightgrey')
    label_path = tk.Label(frame_reader, text='File location', height=2, bg='lightgrey')
    label_control_r = tk.Label(frame_reader, text='File location', height=2, bg='lightgrey')

    # INFORMATION
    button_kill = tk.Button(frame, text='Close', command=Pg.plt_close)
    button_audio = tk.Button(frame, text='Audio', command=Pg.plt_audio)
    button_fft = tk.Button(frame, text='FFT', command=Pg.plt_fft)
    button_freq = tk.Button(frame, text='Frequency', command=Pg.plt_freq)
    entry_time = tk.Scale(frame, from_=0, to=0, orient=tk.HORIZONTAL)
    label_display = tk.Label(frame, text='Information', height=2, bg='lightgrey')
    label_time = tk.Label(frame, text='Timestamp', height=2, bg='lightgrey')
    label_graph = tk.Label(frame, text='Graphs', height=2, bg='lightgrey')
    entry_info = tk.Label(frame)
    entry_display = tk.Label(frame)

    # STREAM
    button_start = tk.Button(frame_serial, text='Start', command=Pg.start)
    button_pause = tk.Button(frame_serial, text='Pause', command=Pg.pause)
    button_stop = tk.Button(frame_serial, text='Stop', command=Pg.stop)
    button_clear = tk.Button(frame_serial, text='Clear', command=Pg.clear)
    entry_delay = tk.Scale(frame_serial, from_=1, to=1000, orient=tk.HORIZONTAL)
    entry_stream = tk.Scale(frame_serial, from_=0, to=256, orient=tk.HORIZONTAL)
    label_delay = tk.Label(frame_serial, text='Delay milliseconds', height=2, bg='lightgrey')
    label_stream = tk.Label(frame_serial, text='Stream Value', height=2, bg='lightgrey')
    label_control_s = tk.Label(frame_serial, text='Stream Control', height=2, bg='lightgrey')

    entry_path.insert(0, Pg.FILEPATH)
    entry_delay.set(Pg.NEXT)
    entry_chunk.set(Pg.CHUNK / 1024)
    entry_speed.set(Pg.FFT_SPS)

    # STREAM
    label_delay.pack(fill=tk.BOTH)
    entry_delay.pack(fill=tk.BOTH)
    label_stream.pack(fill=tk.BOTH)
    entry_stream.pack(fill=tk.BOTH)
    label_control_s.pack(fill=tk.BOTH)
    button_start.pack(fill=tk.BOTH)
    button_pause.pack(fill=tk.BOTH)
    button_stop.pack(fill=tk.BOTH)
    button_clear.pack(fill=tk.BOTH)

    # READER
    label_path.pack(fill=tk.BOTH)
    entry_path.pack(fill=tk.BOTH)
    label_chunk.pack(fill=tk.BOTH)
    entry_chunk.pack(fill=tk.BOTH)
    label_speed.pack(fill=tk.BOTH)
    entry_speed.pack(fill=tk.BOTH)
    label_control_r.pack(fill=tk.BOTH)
    button_read.pack(fill=tk.BOTH)
    button_midi.pack(fill=tk.BOTH)

    # INFORMATION
    label_graph.pack(fill=tk.BOTH)
    button_kill.pack(fill=tk.BOTH)
    button_audio.pack(fill=tk.BOTH)
    button_fft.pack(fill=tk.BOTH)
    button_freq.pack(fill=tk.BOTH)
    label_display.pack(fill=tk.BOTH)
    entry_display.pack(fill=tk.BOTH)
    entry_info.pack(fill=tk.BOTH)
    label_time.pack(fill=tk.BOTH)
    entry_time.pack(fill=tk.BOTH)


    def update():
        entry_display.config(text='Time:%s' % Pg.COUNTER)
        Pg.COUNTER = entry_time.get()
        Pg.COUNTER += 1
        if Pg.COUNTER > Pg.FFT_LENGTH - 1:
            Pg.COUNTER = 0
        Pg.NEXT = entry_delay.get()
        Pg.FFT_SPS = entry_speed.get()
        Pg.FILEPATH = entry_path.get()
        Pg.CHUNK = 1024 * entry_chunk.get()
        entry_time.config(to=Pg.FFT_LENGTH)
        entry_info.config(text=Pg.INFO)
        entry_time.set(Pg.COUNTER)
        if Pg.READY:
            entry_stream.set(int(Pg.spa.single_midi.data[Pg.COUNTER]))
        window.after(Pg.NEXT, update)


    update()
    window.mainloop()
    Pg.json_save()
    Pg.clear()
