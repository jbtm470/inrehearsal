import json
import numpy as np 
import pandas as pd 

import boto3
ddb = boto3.client("dynamodb")
from boto3.dynamodb.conditions import Key, Attr

from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.dispatch_components import AbstractExceptionHandler
from ask_sdk_core.utils import is_request_type, is_intent_name

class LaunchRequestHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        handler_input.response_builder.speak("Welcome to In Rehearsal").set_should_end_session(False)
        return handler_input.response_builder.response    

class CatchAllExceptionHandler(AbstractExceptionHandler):
    def can_handle(self, handler_input, exception):
        return True

    def handle(self, handler_input, exception):
        print(exception)
   
        handler_input.response_builder.speak("Sorry, there was a problem.")
        return handler_input.response_builder.response

class ListScriptIntentHandler(AbstractRequestHandler):

    def can_handle(self, handler_input):
        return is_intent_name("ListScriptIntent")(handler_input)

    def handle(self, handler_input):
        # This Intent will list the scripts available.
        # If a scriptname is passed then the intent will confirm if the script is available to rehearse
        scriptname = handler_input.request_envelope.request.intent.slots['scriptname'].value
        
        # Scan the scripts database & hold the results in a dict object called data
        try:
            data = ddb.scan(
                TableName="Scripts"
            )
        except BaseException as e:
            print(e)
            raise(e)

        speech_text = ""
        script_match = 0

        # build a string of text that Alexa will speak.
        for i in data['Items']:
            st =i['ScriptTitle']['S']
            aut=i['Author']['S']

            if st == scriptname:
                script_match =1

            if speech_text == "":
                pause = ""
            else:
                pause = '<break time=\"1s\"/>'

            speech_text = speech_text + pause + st + ", written by " + aut +"."

        # If no scriptname passed, then recite the list of scripts available 
        # otherwise confirm/deby script availability

        if scriptname == None:
            speech_text = "I have the following scripts." + pause + speech_text
        else:
            if script_match == 1:
                speech_text = "I have the script " + scriptname +"."
            else: 
                speech_text = "I'm sorry, I do not have the script " + scriptname +"."

        # Say the response.    
        handler_input.response_builder.speak(speech_text).set_should_end_session(False)

        handler_input.response_builder.speak(speech_text)
        return handler_input.response_builder.response    

class ReadScriptIntentHandler(AbstractRequestHandler):

    def can_handle(self, handler_input):
        return is_intent_name("ReadScriptIntent")(handler_input)

    def handle(self, handler_input):
        scriptname = handler_input.request_envelope.request.intent.slots['scriptname'].value
        handler_input.response_builder.speak("Lets read "+ scriptname).set_should_end_session(False)
        numAct = '1'
        numScene = '1'
        try:
            data = ddb.scan(
                TableName=scriptname,
                ExpressionAttributeValues={
                    ':act': {
                        'N': "1"
                    },
                    ':scene': {
                        'N': "1"
                    },
                    ':include': {
                        'N': "1"
                    }
                },
                FilterExpression="act = :act and scene = :scene and include = :include",
                ProjectionExpression="act,scene,Line,direction"
            )
        except BaseException as e:
            print(e)
            raise(e)

        pd.DataFrame.from_dict(data)

       
        return handler_input.response_builder.response

class RehearseScriptIntentHandler(AbstractRequestHandler):

    def can_handle(self, handler_input):
        return is_intent_name("RehearseScriptIntent")(handler_input)

    def handle(self, handler_input):
        scriptname = handler_input.request_envelope.request.intent.slots['scriptname'].value
        handler_input.response_builder.speak("Lets rehearse "+ scriptname).set_should_end_session(False)
        numAct = '1'
        numScene = '1'
        try:
            data = ddb.query(
                TableName='Macbeth',
                IndexName="PK1-index",
                KeyConditionExpression="act = :act",
                ExpressionAttributeValues={":act":{"N":"1"}},
                ProjectionExpression="act"
            )
        except BaseException as e:
            print(e)
            raise(e)

        for item in data['Items']:
            print(item)
   
        return handler_input.response_builder.response


sb = SkillBuilder()
sb.add_request_handler(LaunchRequestHandler())
sb.add_exception_handler(CatchAllExceptionHandler())
sb.add_request_handler(ListScriptIntentHandler())
sb.add_request_handler(ReadScriptIntentHandler())
sb.add_request_handler(RehearseScriptIntentHandler())

def handler(event, context):
    return sb.lambda_handler()(event, context)
