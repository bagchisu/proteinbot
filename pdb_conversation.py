#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sun Mar  4 09:18:52 2018

@author: bagchi
"""
import argparse
import webbrowser
import pdb_search as pdb
import watson_developer_cloud
import speech_io
import myconfig
import text_processing as tp

# Set up Conversation service.
conversation = watson_developer_cloud.ConversationV1(
  username = myconfig.WatsonConversation.username,
  password = myconfig.WatsonConversation.password,
  version = '2017-05-26'
)

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

def id_to_name(uid):
    uname = pdb.getUniProtName(uid)
    print uid, uname
    return uname.lower()

def get_exp_method(parameters):
    expMethod = None
    if 'expMethod' in parameters:
        expMethod = parameters['expMethod']
    print "method:", expMethod
    return expMethod

def get_names(uniprotIds):
    # get the recommended names for uniprot ids
    uniprotNames = list(set(map(lambda u: id_to_name(u), uniprotIds)))
    # create a list of up to 3 protein names to speak out
    uniprotNames.sort(key = len)
    user_output = " for "+", ".join(uniprotNames[:3])
    if (len(uniprotNames) > 3):
        user_output += " and "+str(len(uniprotNames) - 3)+" more."
    return user_output

def get_uniprot_ids(parameters):
    uniprotIds = []
    context_proteins = []
    if ('uniprotIds' in parameters) & (parameters['uniprotIds'] != None):
        context_proteins = parameters['uniprotIds']
    if len(context_proteins) > 0:
        for entity in context_proteins:
            uniprotIds.append(entity['value'])
    return uniprotIds

def get_pdb_ids(uniprot_ids, exp_method):
    pdb_ids, rcsb_url = pdb.search(",".join(uniprot_ids), exp_method)
    print ",".join(pdb_ids)
    return list(set(pdb_ids)), rcsb_url

def run_pdb_structure(intent, uniprot_ids, pdbIds):
    user_output = ''
    if (intent == 'structure-exists'):
        user_output = "Yes. " if len(pdbIds) > 0 else "No. "
    user_output += "There" + (" is one structure" if (len(pdbIds) == 1) else " are no structures" if (len(pdbIds) == 0) else (" are "+str(len(pdbIds))+" structures"))
    user_output += get_names(uniprot_ids)
    text_to_speech(user_output)

def run_pdb_ligands(intent, uniprot_ids, pdb_ids):
    ligands = pdb.getLigandNames(pdb_ids)
    print ",".join(ligands)
    if len(ligands) > 0:
        if len(ligands) > 1:
            user_output = "There are " + str(len(ligands)) + " ligands."
        else:
            user_output = "There is one ligand."
        if intent == 'ligand-names':
            ligands.sort(key = len)
            user_output += " "
            user_output += ", ".join(ligands[:3])
            if len(ligands) > 3:
                user_output += " and "+str(len(ligands) - 3)+" more."
    else:
        user_output = "There are no ligands."
    user_output += get_names(uniprot_ids)
    text_to_speech(user_output)

def run_show_details(uniprotIds, url):
    print url
    if url != '':
        text_to_speech("Here are the details " + get_names(uniprotIds))
        webbrowser.open(url)
    else:
        text_to_speech("Sorry, there is no protein information to show.")

def run_release_dates(pdb_ids):
    if pdb_ids:
        release_years = pdb.getReleaseYears(pdb_ids)
        user_output = "Here are the latest release dates: "
        for y in sorted(release_years, reverse=True)[:3]:
            user_output += str(release_years[y]) + " in " + str(y) + "; "
        if len(release_years) > 3:
            user_output += " And more from earlier years."
    else:
        user_output = "There are no structures."
    text_to_speech(user_output)

def run_citation_dates(pdb_ids):
    if pdb_ids:
        citation_years = pdb.getCitationYears(pdb_ids)
        unk = citation_years.pop('null', 0)
        user_output = "Here are the latest citation dates: "
        for y in sorted(citation_years, reverse=True)[:3]:
            user_output += str(citation_years[y]) + " in " + str(y) + "; "
        if len(citation_years) > 3:
            user_output += " And more from earlier years."
        if unk > 0:
            user_output += " Also, "+str(unk)+" with unknown publication year."
    else:
        user_output = "There are no structures."
    text_to_speech(user_output)

def run_citation_titles(pdb_ids):
    if pdb_ids:
        titles = pdb.getCitationTitles(pdb_ids)
        print "\n".join(titles)
        text_to_speech("Here are the citation titles.")
        for t in titles[:3]:
            text_to_speech(t)
        if (len(titles) > 3):
            text_to_speech("And "+str(len(titles)-3)+" more.")
    else:
        text_to_speech("There are no citation titles.")

def run_structure_titles(pdb_ids):
    if pdb_ids:
        titles = pdb.getStructureTitles(pdb_ids)
        print "\n".join(titles)
        text_to_speech("Here are the structure titles.")
        for t in titles[:3]:
            text_to_speech(t)
        if (len(titles) > 3):
            text_to_speech("And "+str(len(titles)-3)+" more.")
    else:
        text_to_speech("There are no structures.")

def run_session():
    # Initialize with empty value to start the conversation.
    user_input = ''
    user_output = ''
    intent = ''
    context = {}
    current_uniprot_ids = []
    current_pdb_ids = []
    current_rcsb_url = ''
    prev_action = ''
    prev_method = None
    
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
        elif intent == 'show-details':
            run_show_details(current_uniprot_ids, current_rcsb_url)
        elif intent == 'release-dates':
            run_release_dates(current_pdb_ids)
        elif intent == 'citation-dates':
            run_citation_dates(current_pdb_ids)
        elif intent == 'citation-titles':
            run_citation_titles(current_pdb_ids)
        elif intent == 'structure-titles':
            run_structure_titles(current_pdb_ids)

        # Update the stored context with the latest received from the dialog.
        context = response['context']
        
        # Check for action flags sent by the dialog.
        if 'actions' in response:
            current_action = response['actions'][0]['name']
            print(current_action)
            parameters = response['actions'][0]['parameters']
            # get the experimental method from entities
            exp_method = get_exp_method(parameters)
            # get the uniprot ids found in the entities (if not found, use current ones)
            uniprot_ids = get_uniprot_ids(parameters)
            valid_proteins = True
            if len(uniprot_ids) > 0:
                current_uniprot_ids = uniprot_ids
            else: # no new proteins detected from response
                if prev_action == current_action and prev_method == exp_method: # if same action is repeated without new protein, assume system didn't understand new protein name
                    text_to_speech("Sorry, I can't recognize the protein name.")
                    valid_proteins = False
            
            if valid_proteins:
                # call the PDB REST service for PDB ids
                current_pdb_ids, current_rcsb_url = get_pdb_ids(current_uniprot_ids, exp_method)
                    
                if current_action == 'PdbStructureFromUniProt':
                    run_pdb_structure(intent, current_uniprot_ids, current_pdb_ids)
                elif current_action == 'PdbLigands':
                    run_pdb_ligands(intent, current_uniprot_ids, current_pdb_ids)
                prev_action = current_action
                prev_method = exp_method
        
        user_input = tp.normalize(speech_to_text())

if __name__ == "__main__":
    global stt_mode
    global tts_mode

    parser = argparse.ArgumentParser(description='Conversation about proteins with PDB.')
    parser.add_argument('-a', '--audio', action="store_true", default=False, help="Full audio mode: equivalent to --listen --speak")
    parser.add_argument('-l', '--listen', action="store_true", default=False, help="Listen and recognize speech to text for input")
    parser.add_argument('-s', '--speak', action="store_true", default=False, help="Synthesize text to speech and speak for output")
    args = parser.parse_args()
    if args.audio:
        stt_mode = True
        tts_mode = True
    else:
        stt_mode = args.listen
        tts_mode = args.speak
    run_session()
