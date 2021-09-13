import json
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
   
        handler_input.response_builder.speak("Sorry, there was a problem. Please try again!!")
        return handler_input.response_builder.response

class ListScriptIntentHandler(AbstractRequestHandler):

    def can_handle(self, handler_input):
        return is_intent_name("ListScriptIntent")(handler_input)

    def handle(self, handler_input):
        try:
            data = ddb.scan(
                TableName="Scripts"
            )
        except BaseException as e:
            print(e)
            raise(e)

        speech_text = ""
        for i in data['Items']:

            st =i['ScriptTitle']['S']
            aut=i['Author']['S']

            if speech_text == "":
                pause = ""
            else:
                pause = '<break time=\"1s\"/>'

            speech_text = speech_text + pause + st + " written by "+ aut

        speech_text = "I have the following scripts." + pause + speech_text
        handler_input.response_builder.speak(speech_text).set_should_end_session(False)


        return handler_input.response_builder.response    

class ReadScriptIntentHandler(AbstractRequestHandler):

    def can_handle(self, handler_input):
        return is_intent_name("ReadScriptIntent")(handler_input)

    def handle(self, handler_input):
        scriptname = handler_input.request_envelope.request.intent.slots['scriptname'].value
        print ("---"+ scriptname)
        handler_input.response_builder.speak("Lets rehearse "+ scriptname).set_should_end_session(False)
        numAct = '1'
        numScene = '1'
        try:
            data = ddb.scan(
                TableName="Macbeth",
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
                FilterExpression="act = :act and scene = :scene and include = :include"
            )
        except BaseException as e:
            print(e)
            raise(e)

        print(data['Items'])

        print(json.dumps((data), indent=4))

        return handler_input.response_builder.response


sb = SkillBuilder()
sb.add_request_handler(LaunchRequestHandler())
sb.add_exception_handler(CatchAllExceptionHandler())
sb.add_request_handler(ListScriptIntentHandler())
sb.add_request_handler(ReadScriptIntentHandler())

def handler(event, context):
    return sb.lambda_handler()(event, context)
