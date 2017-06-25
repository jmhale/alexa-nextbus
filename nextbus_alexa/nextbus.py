# pylint: disable=W0403,W0613,C0301

"""
Lambda function for WMATA's NextBus
"""

import os
from base64 import b64decode
from urllib2 import HTTPError
from helpers import build_speechlet, build_event_response, build_response, \
    get_home_stop, set_home_stop, normalize_output, build_reprompt
import wmata_api as api
import boto3

NUM_BUSES = 5
SKILL_NAME = "Bus Predictor"

## Static messages
NO_STOP_MESSAGE = "You currently do not have a home stop set. \
Please say the seven-digit ID you would like to use for your home stop."
HELP_MESSAGE = "Bus predictor provides real-time arrival information for MetroBuses in the Washington D.C. area. \
To get arrival times, you can say, ask metro bus for arrival times. \
To set your home stop, you can say, ask metro bus to set my home stop as, then say the seven-digit stop id. \
To exit bus predictor, just say, exit. \
What would you like to do?"
EXIT_MESSAGE = "Thank you for using bus predictor. Goodbye!"

def lambda_handler(event, context):
    """ Default entrypoint for Lambda function """
    print("event.session.application.applicationId=" +
          event['session']['application']['applicationId'])

    if "ALEXA_APP_ID" in os.environ:
        encrypted_app_id = os.environ['ALEXA_APP_ID']
        app_id = boto3.client('kms').decrypt(
            CiphertextBlob=b64decode(encrypted_app_id)
        )['Plaintext']
    else:
        raise ValueError("Alexa app ID not provided. Cannot continue.")

    if event['session']['application']['applicationId'] != app_id:
        raise ValueError("Invalid Application ID")

    if event['session']['new']:
        on_session_started({'requestId': event['request']['requestId']},
                           event['session'])

    if event['request']['type'] == "LaunchRequest":
        return on_launch(event['request'], event['session'])
    elif event['request']['type'] == "IntentRequest":
        return on_intent(event['request'], event['session'])
    elif event['request']['type'] == "SessionEndedRequest":
        return on_session_ended(event['request'], event['session'])

def on_session_started(session_started_request, session):
    """Called when the session starts."""
    print("on_session_started requestId=" +
          session_started_request['requestId'] + ", sessionId=" +
          session['sessionId'])

def on_launch(request, session):
    """Called when the user launches the skill without specifying what they want."""
    print("on_launch requestId=" + request['requestId'] +
          ", sessionId=" + session['sessionId'])

    print "request: %s" % request
    resp = get_welcome_response(request, session)
    print "response: %s" % resp
    return resp

def on_intent(request, session):
    """Called when the user specifies an intent for this skill."""
    print("on_intent requestId=" + request['requestId'] +
          ", sessionId=" + session['sessionId'])

    intent = request['intent']
    intent_name = request['intent']['name']

    print intent_name

    if intent_name == "GetBusesIntent":
        return handle_get_buses_request(intent, session)
    elif intent_name == "SetHomeIntent":
        return handle_set_home_stop_request(intent, session)
    elif intent_name == "AMAZON.HelpIntent":
        return handle_help_request(intent, session)
    elif intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
        return handle_session_end_request()

def get_welcome_response(request, session):
    """ Default response """

    user_id = session['user']['userId']
    stop_id = get_home_stop(user_id)

    if stop_id == -1:
        intro = "Welcome to %s for Washington's Metro. %s" % (SKILL_NAME, NO_STOP_MESSAGE)

        reprompt_text = ""
        should_end_session = False
        attributes = {"speech_output": intro}
        return build_response(attributes, build_reprompt(intro, reprompt_text, should_end_session))

    arrivals, reprompt = get_buses_response(stop_id)
    intro = """
<speak>
Welcome to %s for Washington's Metro. \
Your saved stop ID is <say-as interpret-as="digits">%s</say-as>. \
Here are your stop's arrival times: %s
</speak>
""" % (SKILL_NAME, stop_id, arrivals)
    should_end_session = True
    attributes = {"speech_output": intro}
    return build_response(attributes, build_speechlet(intro, should_end_session, ssml=True))

def on_session_ended(request, session):
    """ Called when session is explicitly ended by the user """
    print("on_session_ended requestId=" + request['requestId'] +
          ", sessionId=" + session['sessionId'])

def get_buses_response(stop_id):
    """ Build a get buses response for a stop id """
    try:
        events = api.get_events(stop_id)
    except HTTPError as ex:
        if str(ex.code) == "400":
            response = "I'm sorry. Your stop id is not valid. Please try to set your stop again by saying the seven-digit stop id."
            return response, True

        response = "I'm sorry. There was a problem accessing Metro's system. Please try again later."
        return response, False

    stop_name = events['StopName']

    response = ''

    stop_name = normalize_output(stop_name)

    response += "For the stop at %s: " % stop_name

    for bus_prediction in events['Predictions']:
        response += "%s "% build_event_response(bus_prediction)

    return response, False

## Intent handlers
def handle_get_buses_request(intent, session):
    """ Handles the request for get_buses_intent """
    attributes = {}
    should_end_session = True

    user_id = session['user']['userId']
    stop_id = get_home_stop(user_id)

    if stop_id == -1:
        response = NO_STOP_MESSAGE
        return build_response(attributes, build_speechlet(response, False))

    arrivals, reprompt = get_buses_response(stop_id)

    if reprompt:
        return build_response(attributes, build_speechlet(arrivals, False))

    return build_response(attributes, build_speechlet(arrivals, should_end_session))

def handle_set_home_stop_request(intent, session):
    """ Handles the request for set_home_stop intent """
    attributes = {}
    should_end_session = True

    user_id = session['user']['userId']
    try:
        stop_id = intent['slots']['stop_id']['value']
    except KeyError:
        response = "I'm sorry. I didn't understand your stop id. Please try again"
        return build_response(attributes, build_speechlet(response, False))

    set_resp = set_home_stop(user_id, stop_id)

    if set_resp is not None:
        response = "There was a problem setting your home stop. Please try again later."
    else:
        arrivals, reprompt = get_buses_response(stop_id)
        response = """
<speak>
Your home stop was set successfully to <say-as interpret-as="digits">%s</say-as>. \
Here are your stop's arrival times: %s
</speak>
""" % (stop_id, arrivals)

    return build_response(attributes, build_speechlet(response, should_end_session, ssml=True))

def handle_help_request(intent, session):
    """ Handles a request for the help intent """
    attributes = {"speech_output": HELP_MESSAGE}
    return build_response(attributes, build_reprompt(HELP_MESSAGE, "", False))

def handle_session_end_request():
    """ Handles a exit intent request """
    return build_response({}, build_speechlet(EXIT_MESSAGE, True))
