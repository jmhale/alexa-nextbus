"""
Tests the Lambda function locally
"""

import json
import nextbus_alexa.nextbus as nextbus

with open('input.json') as data_file:
    DATA = json.load(data_file)
    with open('output.json', 'w') as result_file:
        (json.dump(nextbus.lambda_handler(DATA, {}), result_file))
