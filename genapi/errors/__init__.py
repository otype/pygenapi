# -*- coding: utf-8 -*-
"""

    pygenapi

    by hgschmidt

    Copyright (c) 2012 apitrary

"""


class GenapiBaseException(Exception):
    """
        Thrown when a received message is of unknown type
    """

    def __init__(self, message, *args, **kwargs):
        """
            Log the message
        """
        super(GenapiBaseException, self).__init__(*args, **kwargs)
        self.message = message

    def __str__(self):
        """
            Message as string
        """
        return self.message


class NoDictionaryException(GenapiBaseException):
    """
        Thrown when a received message is of unknown type
    """

    def __init__(self, message=None, *args, **kwargs):
        error_message = 'No dictionary provided!'
        if message:
            error_message = message
        super(NoDictionaryException, self).__init__(error_message, *args, **kwargs)


class RiakObjectNotFoundException(GenapiBaseException):
    """
        Thrown when a received message is of unknown type
    """

    def __init__(self, message=None, *args, **kwargs):
        error_message = 'Object with given id not found!'
        if message:
            error_message = message
        super(RiakObjectNotFoundException, self).__init__(error_message, *args, **kwargs)


class RiakObjectIdNotProvidedException(GenapiBaseException):
    """
        Thrown when an object ID was required but not provided
    """

    def __init__(self, message=None, *args, **kwargs):
        error_message = 'No object ID provided! Object ID required.'
        if message:
            error_message = message

        super(RiakObjectIdNotProvidedException, self).__init__(error_message, *args, **kwargs)
