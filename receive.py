#!/usr/bin/python
import pyaudio
import time
import struct
import matplotlib.pyplot as plt

#TODO: get this from argparse
RATE = 44100
FORMAT = pyaudio.paInt16
CHANNELS = 1
#TODO: frames_per_buffer calculation
frames_per_buffer = 128*10

# Define timeouts
SAMPLE_TIMEOUT = 0.1

def chunkify(l, n):
	for i in xrange(0, len(l), n):
		yield l[i:i+n]

def unpack(buffer):
	buf = list(chunkify(buffer,2))
	return  [struct.unpack('h', frame)[0] for frame in buf]

def handle_stream(in_data, frame_count, time_info, status):
	# list of lists
	unpacked_data_list = list(chunkify(unpack(in_data), 128))
	unpacked_data = []
	for data in unpacked_data_list:
		unpacked_data += data
	plt.plot(unpacked_data)
	plt.show()
	return (in_data, pyaudio.paContinue)

# Set up PyAudio
# py_audio = pyaudio.PyAudio()
# py_audio_stream = py_audio.open(format=FORMAT, channels = CHANNELS,
# 								rate=RATE, input=True,
# 								frames_per_buffer=frames_per_buffer,
# 								stream_callback = handle_stream)


def decode_message(message):
	decoded_message = ""

	# take the majority of each set of three
	# to determine what that bit should be
	message_by_majority = ""
	for i in range(0, len(message), 3):
		sum_of_bits = int(message[i]) + int(message[i+1]) + int(message[i+2])
		if sum_of_bits >= 2:
			message_by_majority += "1"
		else:
			message_by_majority += "0"

	char_count = 0
	message_without_parity = ""
	# parity check
	for i in range(0, len(message_by_majority), 8):
		sum_of_bits = 0
		for j in range(7):
			sum_of_bits += int(message_by_majority[i+j])
			message_without_parity += message_by_majority[i+j]
		char_parity = sum_of_bits % 2
		if char_parity != int(message_by_majority[i+7]):
			print "Error: Parity does not match"
			return None

	# rebuild each character from its bits
	decoded_message = ""
	for i in range(0, len(message_without_parity), 7):
		character = 0
		for j in range(7):
			if message_without_parity[i+j] == '1':
				character += 1 << (6-j)
		decoded_message += chr(character)
	return decoded_message


if __name__ == '__main__':
	print "TrackRx Ultrasound listening..."
	py_audio_stream.start_stream()
	while py_audio_stream.is_active():
		time.sleep(SAMPLE_TIMEOUT)
	print "Timed out"