import boto3
ddb = boto3.client("dynamodb")

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
        handler_input.response_builder.speak("Sorry, there was some problem. Please try again!!")
        return handler_input.response_builder.response

class InRehearsalIntentHandler(AbstractRequestHandler):

    def can_handle(self, handler_input):
        return is_intent_name("ListScriptIntent")(handler_input)

    def handle(self, handler_input):
        speech_text = "I have the follwoing scripts"
        handler_input.response_builder.speak(speech_text).set_should_end_session(False)
       
        return handler_input.response_builder.response    

sb = SkillBuilder()
sb.add_request_handler(LaunchRequestHandler())
sb.add_exception_handler(CatchAllExceptionHandler())
sb.add_request_handler(InRehearsalIntentHandler())

def handler(event, context):
    return sb.lambda_handler()(event, context)
