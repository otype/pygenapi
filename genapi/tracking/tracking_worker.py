# -*- coding: utf-8 -*-
"""

    pygenapi

    by hgschmidt

    Copyright (c) 2012 apitrary

"""
import logging
import zmq
from settings.config import ZMQ

def send_tracking_data_asynchronously(tracking_data):
    """
        Creates a connection to the ZMQ server 'trackr', then send the tracking
        data to this server.
    """
    zmq_server = ZMQ['TRACKR_CONNECT_ADDRESS']

    # Establish the ZMQ context, first.
    context = zmq.Context()

    # Establish socket, based on context
    socket = context.socket(zmq.REQ)
    logging.debug('Connecting to ZMQ_SERVER: {}'.format(zmq_server))

    # Connect to ZMQ_SERVER
    socket.connect(zmq_server)

    # Send the tracking data
    logging.debug('Sending to trackr: {}'.format(tracking_data))
    socket.send(tracking_data)

    # close the connection
    socket.close()
