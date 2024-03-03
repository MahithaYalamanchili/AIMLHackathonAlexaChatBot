# -*- coding: utf-8 -*-

# This sample demonstrates handling intents from an Alexa skill using the Alexa Skills Kit SDK for Python.
# Please visit https://alexa.design/cookbook for additional examples on implementing slots, dialog management,
# session persistence, api calls, and more.
# This sample is built using the handler classes approach in skill builder.
import logging
import csv
import requests
import io
import calendar
import ask_sdk_core.utils as ask_utils

from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.dispatch_components import AbstractExceptionHandler
from ask_sdk_core.handler_input import HandlerInput

from ask_sdk_model import Response

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class LaunchRequestHandler(AbstractRequestHandler):
    """Handler for Skill Launch."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool

        return ask_utils.is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "Hello! Welcome to Hackathon project. Would you like to know your zodiac sign or want a store recommendation?"
        repromt_text = "Would you want to look for Store recommendations or your zodiac sign?"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(repromt_text)
                .response
        )


class StoreIntentHandler(AbstractRequestHandler):
    """Handler for Hello World Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("StoreIntent")(handler_input)
        
    def get_store_name(self, row, storeType, storeLocation, storeStatus):
        store_name, store_status, store_type, store_location = row.split(',')
        if storeType == store_type.lower().strip() and storeLocation == store_location.lower().strip() and storeStatus == store_status.lower().strip():
            return store_name
            
    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        slots = handler_input.request_envelope.request.intent.slots
        storeType = slots['StoreType'].value.lower().strip()
        storeStatus = slots['storeStatus'].value.lower().strip()
        storeLocation = slots['StoreCity'].value.lower().strip() 						
        url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSsnW2Wi2WuvFFDODxJ0jRfuH82POj7ig2_9JRYJ1dLrRh2R_6wHKov03a9cD2R6VdRf7UxsUY98S0W/pub?output=csv"
        response = requests.get(url)
        csv_content = response.content
        row = csv_content.decode('utf-8').splitlines()
        rows = row[1:]
        for row in rows:
            storeName = self.get_store_name(row, storeType, storeLocation, storeStatus)
            if storeName is not None:
                speak_output = 'I see you need recommendations for a {storeStatus} {storeType} in {storeLocation}, Here is your recommendation {storeName}.'.format(storeStatus=storeStatus, storeType=storeType, storeLocation=storeLocation, storeName=storeName)
                break
        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask("Happy to help! Do you want to do anthing else. I can find Zodiac sign for different Date of births or I can help with finding other stores in the city")
                .response
        )

class CaptureZodiacSignIntentHandler(AbstractRequestHandler):
    """Handler for Hello World Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("CaptureZodiacSignIntent")(handler_input)

    def filter(self, X):
        date = X.split()
        month = date[0]
        month_as_index = list(calendar.month_abbr).index(month[:3].title())
        day = int(date[1])
        return (month_as_index,day)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        slots = handler_input.request_envelope.request.intent.slots
        year = slots["year"].value
        month = slots["month"].value
        day = slots["day"].value
        url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQvr5YePK4pXg0rUOZYEDCh_KMa8gG-E8o7sFjD_Ngww2L2mpXz6Olak7ARSzd9Ng/pub?gid=1494965002&single=true&output=csv"
        response = requests.get(url)
        csv_content = response.content
        row = csv_content.decode('utf-8').splitlines()
        rows = row[1:] # excluding the first row

        zodiac = ''
        month_as_index = list(calendar.month_abbr).index(month[:3].title())
        usr_dob = (month_as_index,int(day))
        for sign in rows:
            start, end , zodiac = sign.split(',')
            if self.filter(start) <= usr_dob <= self.filter(end):
                zodiac = zodiac
                break

        speak_output = 'I see you were born on the {day} of {month} {year}, which means that your zodiac sign will be {zodiac}.'.format(month=month, day=day, year=year, zodiac=zodiac)


        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask("Happy to help! Do you want to do anthing else. I can find Zodiac sign for other Date of births or I can help with finding different stores in the city")
                .response
        )


class HelpIntentHandler(AbstractRequestHandler):
    """Handler for Help Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("AMAZON.HelpIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "You can say hello to me! How can I help?"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )


class CancelOrStopIntentHandler(AbstractRequestHandler):
    """Single handler for Cancel and Stop Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (ask_utils.is_intent_name("AMAZON.CancelIntent")(handler_input) or
                ask_utils.is_intent_name("AMAZON.StopIntent")(handler_input))

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "Goodbye!"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .response
        )

class FallbackIntentHandler(AbstractRequestHandler):
    """Single handler for Fallback Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("AMAZON.FallbackIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In FallbackIntentHandler")
        speech = "Hmm, I'm not sure. You can say Hello or Help. What would you like to do?"
        reprompt = "I didn't catch that. What can I help you with?"

        return handler_input.response_builder.speak(speech).ask(reprompt).response

class SessionEndedRequestHandler(AbstractRequestHandler):
    """Handler for Session End."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("SessionEndedRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        # Any cleanup logic goes here.

        return handler_input.response_builder.response


class IntentReflectorHandler(AbstractRequestHandler):
    """The intent reflector is used for interaction model testing and debugging.
    It will simply repeat the intent the user said. You can create custom handlers
    for your intents by defining them above, then also adding them to the request
    handler chain below.
    """
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("IntentRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        intent_name = ask_utils.get_intent_name(handler_input)
        speak_output = "You just triggered " + intent_name + "."

        return (
            handler_input.response_builder
                .speak(speak_output)
                # .ask("add a reprompt if you want to keep the session open for the user to respond")
                .response
        )


class CatchAllExceptionHandler(AbstractExceptionHandler):
    """Generic error handling to capture any syntax or routing errors. If you receive an error
    stating the request handler chain is not found, you have not implemented a handler for
    the intent being invoked or included it in the skill builder below.
    """
    def can_handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> bool
        return True

    def handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> Response
        logger.error(exception, exc_info=True)

        speak_output = "Sorry, I Couldn't find that!, do you want to do anthing else. I can find Zodiac for given Date of birth or I can help with finding different stores in the city """

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )

# The SkillBuilder object acts as the entry point for your skill, routing all request and response
# payloads to the handlers above. Make sure any new handlers or interceptors you've
# defined are included below. The order matters - they're processed top to bottom.


sb = SkillBuilder()

sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(CaptureZodiacSignIntentHandler())
sb.add_request_handler(StoreIntentHandler())
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_request_handler(FallbackIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())
sb.add_request_handler(IntentReflectorHandler()) # make sure IntentReflectorHandler is last so it doesn't override your custom intent handlers

sb.add_exception_handler(CatchAllExceptionHandler())

lambda_handler = sb.lambda_handler()