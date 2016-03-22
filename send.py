#!/usr/bin/python

import argparse
import pyaudio

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
FORMAT = pyaudio.paInt16

# Set up PyAudio
py_audio = pyaudio.PyAudio()
py_audio_stream = py_audio.open(format=FORMAT, channels=CHANNELS,
								rate=RATE, output=True)


if __name__ == "__main__":
	print "This is the TrackRx Ultrasound chat test program."
	print "Please press CTRL-C to exit."

	# later, use try-catch for CTRL-C
	while True:
		message = raw_input("> ")
		# send message

