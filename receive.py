#!/usr/bin/python


import pyaudio
import struct
import math
import scipy.signal as signal
import time
import matplotlib.pyplot as plt

#TODO: get this from argparse
RATE = 44100
FORMAT = pyaudio.paInt16
CHANNELS = 1
#TODO: frames_per_buffer calculation
frames_per_buffer = 128*10

# Define timeouts
SAMPLE_TIMEOUT = 0.1


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


INITIAL_TAP_THRESHOLD = 0.010
FORMAT = pyaudio.paInt16 
SHORT_NORMALIZE = (1.0/32768.0)
CHANNELS = 2
RATE = 44100  
INPUT_BLOCK_TIME = 0.01
INPUT_FRAMES_PER_BLOCK = int(RATE*INPUT_BLOCK_TIME)
# if the noise was longer than this many blocks, it's not a 'tap'
MAX_TAP_BLOCKS = 0.15/INPUT_BLOCK_TIME

def get_rms( block ):
    
    count = len(block)/2
    format = "%dh"%(count)
    shorts = struct.unpack( format, block )

    # iterate over the block.
    sum_squares = 0.0
    for sample in shorts:
        # sample is a signed short in +/- 32768. 
        # normalize it to 1.0
        n = sample * SHORT_NORMALIZE
        sum_squares += n*n

    return math.sqrt( sum_squares / count )

class TapTester(object):
    def __init__(self):
        self.pa = pyaudio.PyAudio()
        self.stream = self.open_mic_stream()
        self.tap_threshold = INITIAL_TAP_THRESHOLD
        self.noisycount = MAX_TAP_BLOCKS+1 
        self.quietcount = 0 
        self.errorcount = 0
        self.readinput = []
        self.receive = ''

    def stop(self):
        self.stream.close()

    def find_input_device(self):
        device_index = None            
        for i in range( self.pa.get_device_count() ):     
            devinfo = self.pa.get_device_info_by_index(i)   
            print( "Device %d: %s"%(i,devinfo["name"]) )

            for keyword in ["mic","input"]:
                if keyword in devinfo["name"].lower():
                    print( "Found an input: device %d - %s"%(i,devinfo["name"]) )
                    device_index = i
                    return device_index

        if device_index == None:
            print( "No preferred input found; using default input device." )

        return device_index

    def open_mic_stream( self ):
        device_index = self.find_input_device()

        stream = self.pa.open(   format = FORMAT,
                                 channels = CHANNELS,
                                 rate = RATE,
                                 input = True,
                                 input_device_index = device_index,
                                 frames_per_buffer = INPUT_FRAMES_PER_BLOCK)

        return stream

    def tapDetected(self):
        self.receive += '1'
    def zerodetected(self):
        self.receive += '0'

    def listen(self):
        try:
            block = self.stream.read(INPUT_FRAMES_PER_BLOCK)
            self.readinput.append(block)
            blah = block
        except IOError, e:
            self.errorcount += 1
            print( "(%d) Error recording: %s"%(self.errorcount,e) )
            self.noisycount = 1
            return

        amplitude = get_rms( block )
        if amplitude > self.tap_threshold:
             # noisy block
            self.quietcount = 0
            self.noisycount += 1
            self.tapDetected()

        else:            
            # quiet block.
            self.noisycount = 0
            self.quietcount += 1
            self.zerodetected()

            

if __name__ == "__main__":
    tt = TapTester()
    filename = "blah.txt"
    audioread = open(filename, 'w')
    for i in range(1000):
        tt.listen()
        if tt.quietcount >= 23:
            break

    for i in tt.readinput:
        audioread.write(i)
        #print get_rms(i)
        audioread.write("\n\nblock\n\n\n\n")
        #print len(i)
    audioread.close()
    print tt.receive 
