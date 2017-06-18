"""
Helpers to build Alexa responses
"""

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


def build_speechlet(output, should_end_session):
    """ Builds a speechlet with a card and without reprompt """
    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'shouldEndSession': should_end_session
    }


def build_response(attributes, speechlet_response):
    """ Builds the overall response """
    return {
        'version': '1.0',
        'sessionAttributes': attributes,
        'response': speechlet_response
    }
