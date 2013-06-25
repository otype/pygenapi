# -*- coding: utf-8 -*-
"""

    pygenapi trackr

    by hgschmidt

    Copyright (c) 2012 apitrary

"""
import json
import logging
import zmq
from config import ZMQ
from tracking.google_tracking import send_analytics_data

# Establish ZMQ context
context = zmq.Context()

# Socket to receive messages on
receiver = context.socket(zmq.PULL)

# Bind to the track address
receiver.bind(ZMQ['TRACKR_BIND_ADDRESS'])

# Initial config for logging
logging.basicConfig()

# Set logger name to 'deployr
log = logging.getLogger('trackr')

# Set the default log level
log.setLevel(logging.DEBUG)

log.debug("Starting trackr on: {}".format(ZMQ['TRACKR_BIND_ADDRESS']))
while True:
    # TODO: Strange but first recv() always delivers error! Check this in ZMQ guide!
    # Running a first recv() ... the second one will actually get the message!
    receiver.recv()

    # Receive the tracking data
    message = receiver.recv()

    # Convert message to json
    try:
        tracking_data = json.loads(message)

        # Send the tracking data to Google Analytics
        log.debug("Contacting Google with data: {}".format(tracking_data))
        send_analytics_data(
            remote_ip=tracking_data['remote_ip'],
            user_agent=tracking_data['user_agent'],
            api_id=tracking_data['api_id'],
            api_version=tracking_data['api_version'],
            env=tracking_data['env'],
            entity_name=tracking_data['entity_name'],
            http_method=tracking_data['http_method']
        )
    except ValueError, e:
        # Simply neglect this one ... strangely, all first recv() will cause an error!
        pass
