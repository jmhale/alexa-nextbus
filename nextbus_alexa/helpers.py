"""
Helper functions
"""

import os
import time
import boto3
from botocore.exceptions import ClientError

DAYS_TO_KEEP = 90

if "DYNAMODB_TABLE_NAME" in os.environ:
    TABLE_NAME = os.environ['DYNAMODB_TABLE_NAME']
else:
    raise ValueError("No DynamoDB Table Name Provided. Please set the DYNAMODB_TABLE_NAME env var")


def normalize_output(event_text):
    """ Normalizes the output to sound more natural """
    normalized_text = event_text.replace('St', 'Street')\
                                .replace('+', 'and')\
                                .replace('Rd', 'Road')\
                                .replace('Pl', 'Place')\
                                .replace('Nw', 'Northwest')\
                                .replace('Ne', 'Northeast')\
                                .replace('Sw', 'Southwest')\
                                .replace('Se', 'Southeast')

    return normalized_text

def build_event_response(bus_prediction):
    """ Builds a speech response to a single bus event """

    arrival_minutes = bus_prediction['Minutes']

    if arrival_minutes == 0:
        arrival_text = "is arriving now."
    elif arrival_minutes == 1:
        arrival_text = "will arrive in one minute."
    else:
        arrival_text = "will arrive in %s minutes." % arrival_minutes

    return "A route %s bus, heading %s, %s" % (bus_prediction['RouteID'],
                                               bus_prediction['DirectionText'],
                                               arrival_text)


def build_speechlet(output, should_end_session, ssml=False):
    """ Builds a speechlet """
    if ssml:
        speech_type = "SSML"
        text_type = "ssml"
    else:
        speech_type = "PlainText"
        text_type = "text"
    return {
        "outputSpeech": {
            "type": speech_type,
            text_type: output
        },
        "shouldEndSession": should_end_session
    }


def build_reprompt(output, reprompt_output, should_end_session):
    """ Builds a reprompt speechlet """
    return {
        "outputSpeech": {
            "type": "PlainText",
            "text": output
        },
        "shouldEndSession": should_end_session,
        "reprompt": {
            "outputSpeech": {
                "type": "PlainText",
                "text": reprompt_output
            }
        }
    }


def build_response(attributes, speechlet_response):
    """ Builds the overall response """
    return {
        "version": "1.0",
        "sessionAttributes": attributes,
        "response": speechlet_response
    }

## Helpers for getting/setting home stop
def set_home_stop(user_id, stop_id):
    """ Sets the home stop ID for a user in DynamoDB """
    seconds_to_keep = 86400 * DAYS_TO_KEEP
    expires = str(time.time() + seconds_to_keep).split('.')[0]
    try:
        client = boto3.client('dynamodb')
        client.put_item(
            TableName=TABLE_NAME,
            Item={
                'userId': {'S':user_id},
                'stopId': {'S':stop_id},
                'expires': {'N':expires}
            }
        )
    except ClientError as ex:
        print ex.response
        return ex.response['Error']['Code']

    return None

def get_home_stop(user_id):
    """ Gets the home stop ID for a user in DynamoDB """
    seconds_to_keep = 86400 * DAYS_TO_KEEP
    expires = str(time.time() + seconds_to_keep).split('.')[0]
    client = boto3.client('dynamodb')
    try:
        stop_id = client.get_item(
            TableName=TABLE_NAME,
            Key={
                'userId': {'S':user_id}
            }
        )['Item']['stopId']['S']
    except ClientError as ex:
        print ex.response
        return ex.response['Error']['Code']

    except KeyError as ex:
        print ex
        return -1

    try:
        client.update_item(
            TableName=TABLE_NAME,
            Key={
                'userId':{'S':user_id}
            },
            UpdateExpression="set expires = :t",
            ExpressionAttributeValues={
                ':t': {'N':expires}
            }
        )
    except ClientError as ex:
        print ex.response
        return ex.response['Error']['Code']

    except KeyError as ex:
        print ex
        return -1

    return stop_id

def update_lastused(user_id):
    """ Sets or updates the lastUsed timestamp """
    last_used = str(time.time()).split('.')[0]
    client = boto3.client('dynamodb')

    try:
        client.update_item(
            TableName=TABLE_NAME,
            Key={
                'userId':{'S':user_id}
            },
            UpdateExpression="set lastUsed = :t",
            ExpressionAttributeValues={
                ':t': {'N':last_used}
            }
        )
    except ClientError as ex:
        print ex.response

    except KeyError as ex:
        print ex

def update_call_count(user_id):
    """ Sets or updates the callCount counter """
    client = boto3.client('dynamodb')
    call_count = 0

    try:
        call_count = client.get_item(
            TableName=TABLE_NAME,
            Key={
                'userId': {'S':user_id}
            }
        )['Item']['callCount']['N']
    except ClientError as ex:
        print ex.response

    except KeyError as ex:
        print ex

    call_count = str(call_count + 1)
    try:
        client.update_item(
            TableName=TABLE_NAME,
            Key={
                'userId':{'S':user_id}
            },
            UpdateExpression="set callCount = :t",
            ExpressionAttributeValues={
                ':t': {'N':call_count}
            }
        )
    except ClientError as ex:
        print ex

    except KeyError as ex:
        print ex
