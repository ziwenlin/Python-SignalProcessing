pitches = [
    31, 33, 35, 37, 39, 41, 44, 46, 49, 52, 55, 58, 62, 65, 69, 73, 78, 82, 87, 93, 98, 104, 110, 117, 123, 131, 139,
    147, 156, 165, 175, 185, 196, 208, 220, 233, 247, 262, 277, 294, 311, 330, 349, 370, 392, 415, 440, 466, 494, 523,
    554, 587, 622, 659, 698, 740, 784, 831, 880, 932, 988, 1047, 1109, 1175, 1245, 1319, 1397, 1480, 1568, 1661, 1760,
    1865, 1976, 2093, 2217, 2349, 2489, 2637, 2794, 2960, 3136, 3322, 3520, 3729, 3951, 4186, 4435, 4699, 4978
]


def pitch(num):
    if num == 0:
        return 0
    t = min(pitches, key=lambda x: abs(x - num))
    return pitches.index(t)


pitches.clear()
for i in range(-4 * 12, 4 * 12):
    p = 440.0 * (2.0**(1/12))**i
    pitches.append(p)

if __name__ == "__main__":
    import serial

    com = serial.Serial('COM4')

    while True:
        inp = int(input("Freq: "))
        data = bytearray([pitch(inp)])
        print(int.from_bytes(data, 'big'))
        com.write(data)

    com.close()
