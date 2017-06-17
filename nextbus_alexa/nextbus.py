"""
Lambda function for WMATA's NextBus
"""

import helpers as helpers
import wmata_api as api
import boto3
from botocore.exceptions import ClientError

NUM_BUSES = 5
SKILL_NAME = "WMATA NextBus"

def lambda_handler(event, context):
    """
    Route the incoming request based on type (LaunchRequest, IntentRequest, etc).
    The JSON body of the request is provided in the event parameter.
    """
    print("event.session.application.applicationId=" +
          event['session']['application']['applicationId'])

    """
    Uncomment this if statement and populate with your skill's application ID
    to prevent someone else from configuring a skill that sends requests
    to this function.
    """
    # if (event['session']['application']['applicationId'] !=
    #         "amzn1.echo-sdk-ams.app.[unique-value-here]"):
    #     raise ValueError("Invalid Application ID")


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

def on_launch(launch_request, session):
    """Called when the user launches the skill without specifying what they want."""
    print("on_launch requestId=" + launch_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # Dispatch to your skill's launch
    return get_welcome_response()

def on_intent(intent_request, session):
    """Called when the user specifies an intent for this skill."""
    print("on_intent requestId=" + intent_request['requestId'] +
          ", sessionId=" + session['sessionId'])

    intent = intent_request['intent']
    intent_name = intent_request['intent']['name']

    # Dispatch to your skill's intent handlers
    if intent_name == "get_buses_intent":
        return handle_get_buses_request(intent, session)
    elif intent_name == "set_home_stop_intent":
        return handle_set_home_stop_request(intent, session)

def get_welcome_response():
    """ Default response """
    intro = "Welcome to {}. I am not yet complete.".format(SKILL_NAME)
    should_end_session = True
    attributes = {"speech_output": intro}

    return helpers.build_response(attributes, helpers.build_speechlet_noreprompt(
        SKILL_NAME, intro, should_end_session))

def on_session_ended(session_ended_request, session):
    """
    Called when the user ends the session.
    Is not called when the skill returns should_end_session=true
    """
    print("on_session_ended requestId=" + session_ended_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # add cleanup logic here

def set_home_stop(user_id, stop_id):
    """ Sets the home stop ID for a user in DynamoDB """
    try:
        client = boto3.client('dynamodb')
        client.put_item(
            TableName='alexa-nextbus',
            Item={
                'UserID': user_id,
                'StopID': stop_id
            }
        )
    except ClientError as ex:
        print ex.response
        return ex.response['Error']['Code']

    return None

def get_home_stop(user_id):
    """ Gets the home stop ID for a user in DynamoDB """
    try:
        client = boto3.client('dynamodb')
        stop_id = client.get_item(
            TableName='alexa-nextbus',
            Key={
                'UserID': user_id
            }
        )
    except ClientError as ex:
        print ex.response
        return ex.response['Error']['Code']

    return stop_id

def handle_get_buses_request(intent, session):
    """ Handles the request for get_buses_intent """
    attributes = {}
    should_end_session = True

    stop_id = '1001810'
    events = api.get_events(stop_id)
    stop_name = events['StopName']

    response = ''

    stop_name = helpers.normalize_output(stop_name)

    response += "For the stop at %s: " % stop_name

    for bus_prediction in events['Predictions']:
        response += "%s "% helpers.build_event_response(bus_prediction)

    return helpers.build_response(attributes, helpers.build_speechlet_noreprompt_nocard(
        response, should_end_session))

def handle_set_home_stop_request(intent, session):
    """ Handles the request for set_home_stop intent """
    attributes = {}
    should_end_session = True

    stop_id = intent['slots']['stop_id']['value']
    user_id = session['user']['userId']

    set_resp = set_home_stop(user_id, stop_id)

    if set_resp is not None:
        response = "There was a problem setting your home stop."
    else:
        response = "Your home stop was set successfully."

    return helpers.build_response(attributes, helpers.build_speechlet_noreprompt_nocard(
        response, should_end_session
    ))
