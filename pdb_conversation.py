#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sun Mar  4 09:18:52 2018

@author: bagchi
"""
import argparse
import re
import pdb_search as pdb
import watson_developer_cloud
import speech_io
import myconfig

# Set up Conversation service.
conversation = watson_developer_cloud.ConversationV1(
  username = myconfig.WatsonConversation.username,
  password = myconfig.WatsonConversation.password,
  version = '2017-05-26'
)

numberNames = ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight","nine"]

def text_to_speech(text):
    print '"'+text+'"'
    if tts_mode:
        speech_io.speak(text)

def speech_to_text():
    if stt_mode:
        conf = 0
        while (conf < 0.5):
            print "Listening..."
            (transcript, conf) = speech_io.listen()
            print transcript, conf
        return transcript
    else:
        return raw_input('>> ')

def number_words_to_number(text):
    for val, name in enumerate(numberNames):
        text = re.sub(r'\b'+name+r'\b', str(val), text)
    return re.sub(r'(\d)\s+(\d)', r'\1\2', re.sub(r'(\d)\s+(\d)', r'\1\2', text))

def run_session():
    # Initialize with empty value to start the conversation.
    user_input = ''
    user_output = ''
    intent = ''
    context = {}
    context_proteins = []
    
    # Main input/output loop
    while True:
    
      # Send message to Conversation service.
      response = conversation.message(
        workspace_id = myconfig.WatsonConversation.workspace_id,
        input = {
          'text': user_input
        },
        context = context
      )
    
      # If an intent was detected, print it to the console.
      if response['intents']:
        intent = response['intents'][0]['intent']
    
      # Print the output from dialog, if any.
      if response['output']['text']:
        user_output = response['output']['text'][0]
        text_to_speech(user_output)
    
      # Break out of the loop when conversation is ended.
      if intent == 'end-conversation':
          break

      # Update the stored context with the latest received from the dialog.
      context = response['context']
      
      # Check for action flags sent by the dialog.
      if 'actions' in response:
        current_action = response['actions'][0]['name']
        print(current_action)
        parameters = response['actions'][0]['parameters']
        if (current_action == 'PdbStructureFromUniProt'):
            expMethod = None
            uniprotIds = []
            if 'expMethod' in parameters:
                expMethod = parameters['expMethod']
            if ('uniprotIds' in parameters) & (parameters['uniprotIds'] != None):
                context_proteins = parameters['uniprotIds']
            for entity in context_proteins:
                uniprotIds.append(entity['value'])
    
            print "method:", expMethod
            print "uniprotIds:", ",".join(uniprotIds)
            
            # call the PDB REST service for PDB ids
            pdbIds = pdb.search(",".join(uniprotIds), expMethod)
            user_output = ''
            if (intent == 'structure-exists'):
                user_output = "Yes. " if len(pdbIds) > 0 else "No. "
            user_output += "There" + (" is a structure" if (len(pdbIds) == 1) else " are no structures" if (len(pdbIds) == 0) else (" are "+str(len(pdbIds))+" structures"))
            if (expMethod != None):
                user_output += " with " + expMethod
            text_to_speech(user_output)
      
      user_input = number_words_to_number(speech_to_text())

if __name__ == "__main__":
    global stt_mode
    global tts_mode

    parser = argparse.ArgumentParser(description='Conversation about proteins with PDB.')
    parser.add_argument('-l', '--listen', action="store_true", default=False, help="Listen and recognize speech to text for input")
    parser.add_argument('-s', '--speak', action="store_true", default=False, help="Synthesize text to speech and speak for output")
    args = parser.parse_args()
    stt_mode = args.listen
    tts_mode = args.speak
    run_session()
