"""
Provides helper functions for dealing with the WMATA API
"""

import requests

API_KEY = ''
API_ENDPOINT = 'https://api.wmata.com/'
STOP_ID = ''

def get_events(api_endpoint, api_key, stop_id):
    """ Returns events for a stop ID from the WMATA API """
    api_url = "%sNextBusService.svc/json/jPredictions?api_key=%s&StopID=%s" \
            % (api_endpoint, api_key, stop_id)
    resp = requests.get(api_url)
    return resp.json()
