# -*- coding: utf-8 -*-
"""

    GenAPI

    Response object template

    Copyright (c) 2012 apitrary

"""

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
            Provides a dictionary of the response
        """
        return {
            "statusCode": self.status_code,
            "statusMessage": self.status_message,
            "result": self.result
        }