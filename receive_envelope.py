#!/usr/bin/python


import pyaudio
import struct
import math
import matplotlib.pyplot as plt
import numpy as np
import time
import threading
import Queue

RATE = 44100  
CHANNELS = 1
INPUT_BLOCK_TIME = 0.01
FRAME_SIZE = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1

SAMPLE_TIMEOUT = 0.1
FRAMES_TIMEOUT = 0.1

#just picked a big number
in_frames = Queue.Queue(5000)
frames = Queue.Queue(5000)

start_bit_count = 0
frame_count = 0
message_signal = []
messages = ""
def process_frame():
	global find_start
	global start_bit_count
	global frame_count
	global message_signal
	global messages
	global start_message

	while True:
		try:
			frame = frames.get(False)
			if find_start:
				message_signal = []
				signal = envelope(frame)
				if (sum(signal)/len(signal) > .8):
					start_message += "1"
				else:
					start_message += "0"
				if start_bit_count == 32:
					find_start = False
			else:
				if frame_count != (8*5*num_characters):
					message_signal += frame
					frame_count += 1
				else:
					message_signal = envelope(message_signal)
					message = ""
					for i in range(0, len(message_signal), FRAME_SIZE):
						if (sum(message_signal[i:i+FRAME_SIZE])/FRAME_SIZE > 0.8):
							message += "1"
						else:
							message += "0"
					try:
						messages += decode_message(message) + "\n"
					except TypeError:
						message += "ERRROR!" + "\n"
					# set up to parse another message
					find_start = 1
					start_bit_count = 0
					frame_count = 0
					message_signal = []
				
		except Queue.Empty:
			time.sleep(FRAMES_TIMEOUT)

def decode_message(message):
    decoded_message = ""

    # take the majority of each set of three
    # to determine what that bit should be
    message_by_majority = ""
    for i in range(0, len(message), 5):
        sum_of_bits = int(message[i]) + int(message[i+1]) + int(message[i+2]) + int(message[i+3]) + int(message[i+4])
        if sum_of_bits >= 3:
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

def listen():
	block = stream.read(FRAME_SIZE)
	count = len(block)/2
	format = "%dh"%count
	shorts = struct.unpack(format, block)
	return envelope([s for s in shorts])

def envelope(signal):
	# take absolute value of signal
	for i in range(len(signal)):
		signal[i] = abs(signal[i])

	
	RC = FRAME_SIZE/(RATE*2*3.14)
	dt = 1.0/RATE
	alpha = dt/(dt+RC)
	filtered_signal = [0] * len(signal)
	filtered_signal[0] = signal[0]
	for i in range(1, len(signal)):
		filtered_signal[i] = filtered_signal[i-1] + \
							(alpha*(signal[i]-filtered_signal[i-1]))
	
	# take a moving average with N=3 of signal
	N = 3						
	filtered_signal = np.convolve(filtered_signal, np.ones((N,))/N, mode='valid')
	filtered_signal = filtered_signal.tolist()

	#plt.plot(filtered_signal)
	#plt.show()

	for i in range(len(filtered_signal)):
		if filtered_signal[i] > 100:
			filtered_signal[i] = 1
		else:
			filtered_signal[i] = 0

	# max_sample = max(filtered_signal)
	# final_signal = [sample/max_sample for sample in filtered_signal]
	# for i in range(len(final_signal)):
	# 	if final_signal[i] > .5:
	#  		final_signal[i] = 1
	# 	else:
	#  		final_signal[i] = 0
	# return final_signal
	return filtered_signal

sample_cnt = 0
signal = []

find_start = True
processes = [process_frame]
threads = []
for process in processes:
	thread = threading.Thread(target=process)
	thread.daemon = True
	thread.start()

def callback(data, frame_count, time_info, status):
	global sample_cnt
	global signal
	global find_start
	count = len(data)/2
	format = "%dh"%count
	block = struct.unpack(format, data)
	block = [b for b in block]
	sample_cnt += 1
	#signal += block
	if not frames.full():
		frames.put(block, False)
	return (data, pyaudio.paContinue)
	

num_characters = 0
if __name__ == "__main__":
	num_characters = len(raw_input("> "))
	py_audio = pyaudio.PyAudio()
	stream = py_audio.open(format=FORMAT, channels=CHANNELS, rate=RATE,
							frames_per_buffer=FRAME_SIZE,
							input=True, stream_callback=callback)
	
	# for i in range(300):
	# 	signal += listen()
	stream.start_stream()
	while stream.is_active():
		time.sleep(SAMPLE_TIMEOUT)
		if sample_cnt > ((5*8*num_characters)+32)*15+100:
			stream.stop_stream()
	print messages

	
