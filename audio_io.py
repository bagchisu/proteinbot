#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sat Mar 10 12:17:13 2018

@author: bagchi
from https://github.com/jeysonmc/python-google-speech-scripts/blob/master/stt_google.py
"""

import pyaudio
import wave
import audioop
from collections import deque
import math


# Microphone stream config.
CHUNK = 1024  # CHUNKS of bytes to read each time from mic
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
THRESHOLD = 1000  # The threshold intensity that defines silence
                  # and noise signal (an int. lower than THRESHOLD is silence).

SILENCE_LIMIT = 1  # Silence limit in seconds. The max ammount of seconds where
                   # only silence is recorded. When this time passes the
                   # recording finishes and the file is delivered.

PREV_AUDIO = 0.5  # Previous audio (in seconds) to prepend. When noise
                  # is detected, how much of previously recorded audio is
                  # prepended. This helps to prevent chopping the beggining
                  # of the phrase.

__AUDIO_IO_P__ = None

def create_rec_stream():
    global __AUDIO_IO_P__
    stream = __AUDIO_IO_P__.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)
    return stream

def init_audio():
    global __AUDIO_IO_P__

    __AUDIO_IO_P__ = pyaudio.PyAudio()
    stream = create_rec_stream()
    
    """ Gets average audio intensity of your mic sound. You can use it to get
        average intensities while you're talking and/or silent. The average
        is the avg of the 20% largest intensities recorded.
    """
    num_samples = 50
    values = [math.sqrt(abs(audioop.avg(stream.read(CHUNK), 4))) 
              for x in range(num_samples)] 
    values = sorted(values, reverse=True)
    r = sum(values[:int(num_samples * 0.2)]) / int(num_samples * 0.2)
    stream.close()
    return r

def listen_for_speech(threshold=THRESHOLD):
    stream = create_rec_stream()
    """
    Listens to Microphone, extracts phrases from it. A "phrase" is sound 
    surrounded by silence (according to threshold). num_phrases controls
    how many phrases to process before finishing the listening process 
    (-1 for infinite). 
    """

    audio2send = []
    cur_data = ''  # current chunk  of audio data
    rel = RATE/CHUNK
    slid_win = deque(maxlen=SILENCE_LIMIT * rel)
    #Prepend audio from 0.5 seconds before noise was detected
    prev_audio = deque(maxlen=PREV_AUDIO * rel) 
    started = False

    while (True):
        try:
            cur_data = stream.read(CHUNK)
        except IOError as ex:
            if ex[1] != pyaudio.paInputOverflowed:
                raise
            cur_data = '\x00' * CHUNK

        slid_win.append(math.sqrt(abs(audioop.avg(cur_data, 4))))
        #print slid_win[-1]
        if(sum([x > THRESHOLD for x in slid_win]) > 0):
            if(not started):
                started = True
            audio2send.append(cur_data)
        elif (started is True):
            # Return the recorded sound
            stream.close()
            data = ''.join(list(prev_audio) + audio2send)  
            return data;
        else:
            prev_audio.append(cur_data)
            
def save_speech(data, filename):    
    global __AUDIO_IO_P__
    """ Saves mic data to temporary WAV file. Returns filename of saved 
        file """
    # writes data to WAV file
    wf = wave.open(filename + '.wav', 'wb')
    wf.setnchannels(1)
    wf.setsampwidth(__AUDIO_IO_P__.get_sample_size(pyaudio.paInt16))
    wf.setframerate(RATE)
    wf.writeframes(data)
    wf.close()
    return filename + '.wav'

def load_play_speech(filename):
    global __AUDIO_IO_P__
    wf = wave.open(filename + '.wav', 'rb')
    # open stream based on the wave object which has been input.
    stream = __AUDIO_IO_P__.open(format =
                __AUDIO_IO_P__.get_format_from_width(wf.getsampwidth()),
                channels = wf.getnchannels(),
                rate = wf.getframerate(),
                output = True)
    
    # read data (based on the chunk size)
    data = wf.readframes(CHUNK)

    # play stream (looping from beginning of file to the end)
    while data != '':
        # writing to the stream is what *actually* plays the sound.
        stream.write(data)
        data = wf.readframes(CHUNK)
    
    # cleanup stuff.
    stream.close()    

def play_speech(data):
    global __AUDIO_IO_P__
    # open stream based on the wave object which has been input.
    stream = __AUDIO_IO_P__.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    output=True,
                    frames_per_buffer=CHUNK)
    stream.write(data)
    stream.close()
    
def terminate_audio():
    global __AUDIO_IO_P__
    __AUDIO_IO_P__.terminate()
    
if(__name__ == '__main__'):
    print "initializing audio -- please don't speak now..."
    silence_threshold = init_audio()
    while (True):
        print "Listening..."
        data = listen_for_speech(silence_threshold) # listen to mic.
        print "Playing back and saving."
        save_speech(data, "temp")
        load_play_speech("temp")

