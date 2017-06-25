# WMATA NextBus Predictor for Amazon's Echo

Master|[![Build Status](https://travis-ci.org/jmhale/alexa-nextbus.svg?branch=master)](https://travis-ci.org/jmhale/alexa-nextbus)
Develop|[![Build Status](https://travis-ci.org/jmhale/alexa-nextbus.svg?branch=develop)](https://travis-ci.org/jmhale/alexa-nextbus)

This app provides real-time bus arrival information on a Amazon's Echo, using WMATA's public API.

It is intended to be deployed as a Lambda function on AWS and uses DynamoDB to store users' home stop ID, based on their Amazon Echo user ID.

Before the initial "Get stop" request is made, a home stop ID must be set, using the SetHomeIntent intent.

Note that you will need the following environment variables to be set for the app to function:

- `WMATA_API_KEY`: Your developer's API key from https://developer.wmata.com/
- `ALEXA_APP_ID`: The ID of your Alexa application. This is found at https://developer.amazon.com/

If you save these env vars in your Lambda config, I highly recommend that you use KMS to encrypt them, as they are both potentially sensitive pieces of information.

Disclaimer: This is an independently developed app and is in no way, shape or form connected to, affiliated with, or maintained by the Washington Metropolitan Area Transit Authority
