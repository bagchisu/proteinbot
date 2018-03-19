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
        audio_io.save_speech(in_data, 'temp_stt')
        with open('temp_stt.wav', 'rb') as audio_rec_file:
            stt = _SPEECH_TO_TEXT_.recognize(model=myconfig.WatsonSpeechToText.model,customization_id=myconfig.WatsonSpeechToText.customization_id,audio=audio_rec_file,content_type='audio/wav')
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
    
    with open('temp_tts.wav', 'wb') as audio_play_file:
        audio_play_file.write(_TEXT_TO_SPEECH_.synthesize(transcript, accept='audio/wav',voice=myconfig.WatsonTextToSpeech.voice))
    
    audio_io.load_play_speech('temp_tts')
    _last_session_time_ = time.time()
    
if(__name__ == '__main__'):
    voices = [
    'de-DE_BirgitVoice',
    'de-DE_DieterVoice',
    'en-GB_KateVoice',
    'en-US_AllisonVoice',
    'en-US_LisaVoice',
    'en-US_MichaelVoice',
    'es-ES_LauraVoice',
    'es-ES_EnriqueVoice',
    'es-LA_SofiaVoice',
    'es-US_SofiaVoice',
    'fr-FR_ReneeVoice',
    'it-IT_FrancescaVoice',
    'ja-JP_EmiVoice',
    'pt-BR_IsabelaVoice'
    ]
    while (True):
#        (t,c) = listen()
        t = raw_input('>> ')
        c = 1
#        print t, c
        if c > 0.5:
            for v in voices:
                myconfig.WatsonTextToSpeech.voice = v
                print v
                speak(t)
     
    
    
