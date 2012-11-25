# -*- coding: utf-8 -*-
"""

    pygenapi

    by hgschmidt

    Copyright (c) 2012 apitrary

"""

class BaseException(Exception):
    """
        Thrown when a received message is of unknown type
    """

    def __init__(self, message, *args, **kwargs):
        """
            Log the message
        """
        super(BaseException, self).__init__(*args, **kwargs)
        self.message = message

    def __str__(self):
        """
            Message as string
        """
        return self.message


class RiakObjectNotFoundException(BaseException):
    """
        Thrown when a received message is of unknown type
    """
    pass