# -*- coding: utf-8 -*-
"""

    GenAPI

    Response object template

    Copyright (c) 2012 apitrary

"""
import json


class Response(object):
    """
        Response template. Using get_data(), this method will deliver a
        response object of following layout:

        {
            "statusCode": 200,
            "statusMessage": "Everything went well",
            "result": {
                "_id": "8890usd80hjhsdv",
                "_data": {"firstName": "Max", "lastName": "Petersen"}
            }
        }

        Or, with multiple results:

        {
            "statusCode": 200,
            "statusMessage": "Everything went well",
            "result": [
                {
                    "_id": "8890usd80hjhsdv",
                    "_data": {"firstName": "Max", "lastName": "Petersen"}
                },
                {
                    "_id": "888shvnbsodvg3v",
                    "_data": {"firstName": "Karl", "lastName": "Watson"}
                }
            ]
        }

    """

    def __init__(self, status_code, status_message, result):
        """
            We ALWAYS need these three values: statusCode, status_message, result
        """
        self.status_code = status_code
        self.status_message = status_message
        self.result = result

    def __str__(self):
        return 'Response(status_code={}, status_message="{}", result="{}")'.format(
            self.status_code,
            self.status_message,
            self.result
        )

    def __repr__(self):
        return u'Response(status_code={}, status_message="{}", result="{}")'.format(
            self.status_code,
            self.status_message,
            self.result
        )

    def get_data(self):
        """
            Provides a correctly encoding string of the response
        """
        return json.dumps({"result": self.result}).decode('unicode-escape')


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
