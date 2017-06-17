"""
Provides helper functions for dealing with the WMATA API
"""

import urllib2
import json
from config import WMATA_API_KEY as api_key

API_ENDPOINT = 'https://api.wmata.com/'

def get_events(stop_id):
    """ Returns events for a stop ID from the WMATA API """
    api_url = "%sNextBusService.svc/json/jPredictions?api_key=%s&StopID=%s" \
            % (API_ENDPOINT, api_key, stop_id)

    req = urllib2.Request(api_url)
    return json.loads(urllib2.urlopen(req).read())
