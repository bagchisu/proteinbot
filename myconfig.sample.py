#Watson Conversation
#https://www.ibm.com/watson/developercloud/conversation.html
class WatsonConversation:
	username = ''
	password = ''
	workspace_id = ''

#Watson Speech to Text
#https://www.ibm.com/watson/developercloud/speech-to-text.html
class WatsonSpeechToText:
	password = ''
	username = ''
	url = 'https://stream.watsonplatform.net/speech-to-text/api'
	model = 'en-US_BroadbandModel'
	customization_id = ''

#Watson Text to Speech
#https://www.ibm.com/watson/developercloud/text-to-speech.html
class WatsonTextToSpeech:
	password =''
	username = ''
	voice = 'en-US_LisaVoice'
	url = 'https://stream.watsonplatform.net/text-to-speech/api'