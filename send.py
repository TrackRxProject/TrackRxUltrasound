#!/usr/bin/python

import argparse
import math
import matplotlib.pyplot as plt
import pyaudio
import struct
import numpy


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
				default = 256, help='Set the chunk size (default:256)')
args = parser.parse_args()
RATE = args.rate
FREQ = args.freq
CHANNELS = args.channels
FRAME_LENGTH = args.framelen
CHUNK = args.chunk
FORMAT = pyaudio.paFloat32

# Set up PyAudio
py_audio = pyaudio.PyAudio()
py_audio_stream = py_audio.open(format=FORMAT, channels=CHANNELS,
								rate=RATE, output=True)

START_BYTE_STRING = "11111111"
STOP_BYTE_STRING = "00000000"

def pattern_generator(message):
    string_message = []
    for char in message:
        string_message.append(bin(ord(char))[2:]);

    pattern = ''
    for char in string_message:
        parity = 0
        for bit in char:
            pattern += (bit+bit+bit)
            parity += int(bit)
        parity = parity % 2
        pattern += str(parity) + str(parity) + str(parity)
    pattern = START_BYTE_STRING + pattern + STOP_BYTE_STRING
    print pattern
    return pattern

def tone_generator(pattern, freq, datasize, rate):
    tone = numpy.array([])
    for bit in pattern:
        amp = 100 if (bit == '1') else 0
        sine = sine_generator(freq, datasize, rate, amp)
        tone = numpy.concatenate([tone,sine])
    tone = tone * .25
    return tone

def fgenerate(message, freq, datasize, rate):
    pattern = pattern_generator(message)
    tone = tone_generator(pattern, freq, datasize, rate)
    return tone

def sine_generator(frequency, datasize, rate, amp):
    factor = float(frequency) * (math.pi * 2) / rate
    return amp*numpy.sin(numpy.arange(datasize) * factor)

if __name__ == '__main__':
    #t = fgenerate('a',20000, 441, 44100)
    while True:
        #t = tone_generator('11001100', 10000, 441, 44100)
        t = fgenerate('b', 20000, 441, 44100)
        py_audio_stream.write(t.astype(numpy.float32).tostring())

    #py_audio_stream.close()
    #py_audio.terminate()
    # print "This is the TrackRx Ultrasound chat test program."
	# print "Please press CTRL-C to exit."
	# # later, use try-catch for CTRL-C
	# while True:
	# 	message = raw_input("> ")
	# 	# send message

    
#while True:
# t = fgenerate('a', 15000)
# plt.plot(t)
# plt.show()
# while True:
#     output = prepare_pyaudio_buffer(t)
# #plt.plot(t)
# #plt.show()
#     py_audio_stream.write(output)

