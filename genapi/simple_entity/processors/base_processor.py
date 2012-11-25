# -*- coding: utf-8 -*-
"""

    pygenapi

    by hgschmidt

    Copyright (c) 2012 apitrary

"""
import logging
from response import Response

class BaseProcessor(object):
    """
        Base Processor settings
    """

    def __init__(self, headers, riak_client, bucket, bucket_name):
        """
            Simple init method ...
        """
        super(BaseProcessor, self).__init__()

        # Set the HTTP Headers
        self.headers = headers

        # Set the Riak client, bucket name and bucket
        self.riak_client = riak_client
        self.bucket_name = bucket_name
        self.bucket = bucket

    def has_valid_headers(self):
        """
            Requires all types:
            - Content-Type == application/json
            - Accept == application/json
        """
        return self.has_valid_content_type() and self.has_valid_accept_type()

    def has_valid_content_type(self):
        """
            Check if given request has content-type 'application/json'
        """
        return self.get_key_from_header('Content-Type') == 'application/json'

    def has_valid_accept_type(self):
        """
            Check if given request has content-type 'application/json'
        """
        return self.get_key_from_header('Accept') == 'application/json'

    def get_key_from_header(self, key_name):
        """
            Read a given key from header of given request
        """
        for k, v in self.headers.get_all():
            if k == key_name:
                return v
        return None
