# -*- coding: utf-8 -*-
"""

    pygenapi

    by hgschmidt

    Copyright (c) 2012 apitrary

"""
import logging
import zmq
from settings.config import ZMQ

class TrackrService(object):
    """
        Handles all calls to Trackr.
    """

    def __init__(self, zmq_server=None):
        """
            Setup the Trackr (ZMQ) server
        """
        super(TrackrService, self).__init__()

        self.zmq_server = ZMQ['TRACKR_CONNECT_ADDRESS']
        if zmq_server:
            self.zmq_server = zmq_server


    def send_tracking_data_asynchronously(self, tracking_data):
        """
            Creates a connection to the ZMQ server 'trackr', then send the tracking
            data to this server.
        """
        # Establish the ZMQ context, first.
        context = zmq.Context()

        # Establish socket, based on context
        socket = context.socket(zmq.REQ)
        logging.debug('Connecting to ZMQ_SERVER: {}'.format(self.zmq_server))

        # Connect to ZMQ_SERVER
        socket.connect(self.zmq_server)

        # Send the tracking data
        logging.debug('Sending to trackr: {}'.format(tracking_data))
        socket.send(tracking_data)

        # close the connection
        socket.close()

        # Terminate context
        context.term()
        del context
