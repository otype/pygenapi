# -*- coding: utf-8 -*-
"""

    pygenapi

    by hgschmidt

    Copyright (c) 2012 - 2013 apitrary

"""
import json

class GoogleTrackingData(object):
    """
        A tracking data object which can be used to send the tracking information from a given
        request to Google Analytics (or Piwik).
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
