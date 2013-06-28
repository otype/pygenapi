# -*- coding: utf-8 -*-
"""

    pygenapi

    by hgschmidt

    Copyright (c) 2012 apitrary

"""
import json
import zmq
import logging

ZMQ = {
    'TRACKR_CONNECT_ADDRESS': "tcp://localhost:5555",  # ZMQ_SERVER is running locally (for now).
    'TRACKR_BIND_ADDRESS': "tcp://*:5555"   # ZMQ_SERVER is running locally (for now).
}


class TrackingService(object):
    """
        Provide calls for sending tracking data to Google Analytics, etc.
    """

    def send_data_to_trackr(self, tracking_data):
        """
            Send tracking data to Trackr method
        """
        trackr_service = TrackrService()
        trackr_service.send_tracking_data_asynchronously(tracking_data=str(tracking_data.as_json()))


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


class GoogleTrackingData(object):
    """
        A tracking data object which can be used to send the tracking information from a given
        request to Google Analytics.
    """

    def __init__(self, request, user_agent, api_id, api_version, env, entity_name):
        """
            Load all tracking information into this object
        """
        super(GoogleTrackingData, self).__init__()

        self.remote_ip = ""
        self.http_method = ""

        if request is not None:
            self.remote_ip = request.headers.get('X-Forwarded-For')
            self.http_method = request.method

        self.user_agent = user_agent
        self.api_id = api_id
        self.api_version = api_version
        self.env = env
        self.entity_name = entity_name

    def as_json(self):
        """
            Return this Google tracking data as JSON object.
        """
        return json.dumps(self.__dict__)
