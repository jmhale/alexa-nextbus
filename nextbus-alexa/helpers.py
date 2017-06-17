"""
Helpers to build Alexa responses
"""

def build_speechlet_response(title, output, reprompt_text, should_end_session):
    """ Builds a speechlet with a card """
    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'card': {
            'type': 'Simple',
            'title': title,
            'content': output
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': reprompt_text
            }
        },
        'shouldEndSession': should_end_session
    }

def build_speechlet_noreprompt(title, output, should_end_session):
    """ Builds a speechlet with a card and without reprompt """
    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'card': {
            'type': 'Simple',
            'title': title,
            'content': output
        },
        'shouldEndSession': should_end_session
    }


def build_speechlet_nocard(output, reprompt_text, should_end_session):
    """ Builds a speechlet without a card """
    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': reprompt_text
            }
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
