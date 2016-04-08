#!/usr/bin/python

import argparse
import math
import matplotlib.pyplot as plt
import pyaudio
import struct
import time


# Set the parameters for sending a message
parser = argparse.ArgumentParser(description='Send characters using ASK.')
parser.add_argument('--rate', '-r', dest='rate', type=int,
				default = 44100, help='Set the rate (default:44100)')
parser.add_argument('--freq', '-f', dest='freq', type=int,
				default = 19100, help='Set the frequency (default:19100)')
parser.add_argument('--channels', '-c', dest='channels', type=int,
				default = 1, help='Set the number of channels (default:1)')
parser.add_argument('--framelen', '-l', dest='framelen', type=int,
				default = 3, help='Set the frame length (default:3)')
parser.add_argument('--chunk', '-k', dest='chunk', type=int,
				default = 1024, help='Set the chunk size (default:1024)')
args = parser.parse_args()
RATE = args.rate
FREQ = args.freq
CHANNELS = args.channels
FRAME_LENGTH = args.framelen
CHUNK = args.chunk
FORMAT = pyaudio.paInt16

# Set up PyAudio
py_audio = pyaudio.PyAudio()
py_audio_stream = py_audio.open(format=FORMAT, channels=CHANNELS,
								rate=RATE, output=True)

START_BYTE_STRING = "1111111111111111111111111111111111111111"
STOP_BYTE_STRING = "00000000"

def pattern_generator(message):
    string_message = []
    #message = str(len(message)) + message
    for char in message:
        char_rep = bin(ord(char))[2:]
        while len(char_rep) < 7:
            char_rep = '0' + char_rep
        string_message.append(char_rep);

    pattern = ''
    for char in string_message:
        parity = 0
        for bit in char:
            pattern += (bit+bit+bit+bit+bit)
            parity += int(bit)
        parity = parity % 2
        pattern += str(parity) + str(parity) + str(parity)
        pattern += str(parity) + str(parity)
    pattern = START_BYTE_STRING + pattern + STOP_BYTE_STRING
    return pattern

def tone_generator(pattern, freq, datasize, rate):
    tone = []
    offset = 0
    for bit in pattern:
        amp = 12000 if (bit == '1') else 0
        sine = sine_generator(freq, datasize, rate, amp, offset)
        tone += sine
        offset += datasize
    #plt.plot(tone)
    #plt.show()
    return [struct.pack('h', frame) for frame in tone]

def send_message(message, freq, datasize, rate):
    pattern = pattern_generator(message)
    tone = tone_generator(pattern, freq, datasize, rate)
    tone = ''.join(tone)
    py_audio_stream.write(tone)

def sine_generator(frequency, datasize, rate, amp, offset):
    factor = float(frequency) * (math.pi * 2) / rate
    sine = []
    for i in range(datasize):
        sine.append(int(amp*math.sin((i+offset)*factor)))
    return sine

if __name__ == '__main__':
    print "This is the TrackRx Ultrasound chat test program."
    print "Please press CTRL-C to exit."
	# later, use try-catch for CTRL-C
    message = raw_input("> ")
    for i in range(15):
        send_message(message, FREQ, CHUNK, RATE)
        #time.sleep(1)
