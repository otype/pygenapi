# -*- coding: utf-8 -*-
"""

    GenAPI

    Error Response object template

    Copyright (c) 2012 apitrary

"""
import json
from simple_entity.handler_helpers import get_current_time_formatted


class ErrorResponse(object):
    """
        Error Response template. Using get_data(), this method will deliver a
        response object of following layout:

        {
          "error" : {
            "message" : "Invalid API Key.",
            "incident_time" : "25 Jun 2013 17:33:40 +0000"
          }
        }
    """

    def __init__(self, error_message):
        self.error_message = error_message

    def __str__(self):
        return 'ErrorResponse(error_message="{}")'.format(self.error_message)

    def __repr__(self):
        return u'ErrorResponse(error_message="{}")'.format(self.error_message)

    def get_data(self):
        resp = {
            "error": {
                "incident_time": get_current_time_formatted(),
                "message": self.error_message
            }
        }

        return json.dumps(resp).decode('unicode-escape')

