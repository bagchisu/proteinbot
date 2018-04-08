#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sat Mar 10 19:58:57 2018

@author: bagchi
"""

import time
import audio_io
#import json
from watson_developer_cloud import SpeechToTextV1
from watson_developer_cloud import TextToSpeechV1

import myconfig

_SPEECH_TO_TEXT_ = SpeechToTextV1(
    username=myconfig.WatsonSpeechToText.username,
    password=myconfig.WatsonSpeechToText.password,
    url=myconfig.WatsonSpeechToText.url)

_TEXT_TO_SPEECH_ = TextToSpeechV1(
    username=myconfig.WatsonTextToSpeech.username,
    password=myconfig.WatsonTextToSpeech.password)

#print(json.dumps(_TEXT_TO_SPEECH_.voices(), indent=2))
_SILENCE_THRESHOLD_ = None
_last_session_time_ = 0

LISTEN_THRESHOLD = 6 # seconds

def _trigger_word_detected_(data):
    #TODO: local trigger word detection
    return True

def _calibrate_silence_():
    global _SILENCE_THRESHOLD_
    print "initializing audio -- please don't speak now..."
    _SILENCE_THRESHOLD_ = audio_io.init_audio()
    print "silence threshold=", _SILENCE_THRESHOLD_
    print "...done. Thank you."

def listen():
    global _SPEECH_TO_TEXT_
    global _SILENCE_THRESHOLD_
    global _last_session_time_
    
    if (_SILENCE_THRESHOLD_ == None):
        _calibrate_silence_()
    
    try:    
        in_data = audio_io.listen_for_speech(_SILENCE_THRESHOLD_)
    except:
        audio_io.terminate_audio()
        raise
    
    if (time.time() - _last_session_time_ < LISTEN_THRESHOLD or _trigger_word_detected_(in_data)):
        print "Recognizing..."
        stt = _SPEECH_TO_TEXT_.recognize(model=myconfig.WatsonSpeechToText.model,customization_id=myconfig.WatsonSpeechToText.customization_id,audio=in_data,content_type='audio/l16;rate=16000;channels=1')
        #print(json.dumps(stt, indent=2))
        try:
            stt_result = stt['results'][stt['result_index']]['alternatives'][0]
            stt_transcript = stt_result['transcript']
            stt_confidence = stt_result['confidence']
        except IndexError:
            stt_transcript = "Sorry, I couldn't recognize what you said."
            stt_confidence = 0.0
        _last_session_time_ = time.time()
        return (stt_transcript, stt_confidence)
    else:
        return ("", 0)
        

def speak(transcript):
    global _TEXT_TO_SPEECH_
    global _SILENCE_THRESHOLD_
    global _last_session_time_
    
    if (_SILENCE_THRESHOLD_ == None):
        _calibrate_silence_()
    
    out_data = _TEXT_TO_SPEECH_.synthesize(transcript, accept='audio/l16;rate=16000;channels=1',voice=myconfig.WatsonTextToSpeech.voice)
    audio_io.play_speech(out_data)
    _last_session_time_ = time.time()
    
if(__name__ == '__main__'):
    while (True):
        print "Listening..."
        (t,c) = listen()
        print t, c
        if c > 0.5:
            print '"'+t+'"'
            speak(t)     
    
    
