# pylint: disable=W0403
"""
Provides helper functions for dealing with the WMATA API
"""

import os
import urllib.request, urllib.error, urllib.parse
import json
from base64 import b64decode
import boto3

API_ENDPOINT = 'https://api.wmata.com/'

class NoApiKeyException(Exception):
    """ Exception class for no API key errors """
    pass

def get_events(stop_id):
    """ Returns events for a stop ID from the WMATA API """
    if "WMATA_API_KEY" in os.environ:
        encrypted_api_key = os.environ['WMATA_API_KEY']
        api_key = boto3.client('kms').decrypt(
            CiphertextBlob=b64decode(encrypted_api_key)
        )['Plaintext']
    else:
        raise NoApiKeyException("WMATA API key not provided")


    api_url = "%sNextBusService.svc/json/jPredictions?api_key=%s&StopID=%s" \
            % (API_ENDPOINT, api_key, stop_id)

    req = urllib.request.Request(api_url)
    return json.loads(urllib.request.urlopen(req).read())
