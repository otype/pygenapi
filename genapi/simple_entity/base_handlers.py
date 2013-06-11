# -*- coding: utf-8 -*-
"""

    GenAPI

    Copyright (c) 2012 - 2013 apitrary

"""
import logging
import riak
import tornado.ioloop
import tornado.web
import tornado.escape
from tornado import httpclient
import tornado.httpserver
import tornado.httputil
from tornado.options import options
from errors import NoDictionaryException
from simple_entity.handler_helpers import get_current_time_formatted
from models.response import Response


class BaseHandler(tornado.web.RequestHandler):
    """
        The most general handler class. Should be sub-classed by all consecutive
        handler classes.
    """

    def __init__(self, application, request, **kwargs):
        """
            Base initializer! Sets up:
            - the riak (sync) client,
            - the async http client for async Riak calls,
            - enforces application/json for all requests
        """
        super(BaseHandler, self).__init__(application, request, **kwargs)

        # Setup the Async HTTP client for calling Riak asynchronously
        self.async_http_client = tornado.httpclient.AsyncHTTPClient()

        # Setup Riak base URLs for AsyncHttpClient
        self.riak_protocol = 'http://'
        self.riak_url = '{protocol}{node}:{port}'.format(
            protocol=self.riak_protocol,
            node=options.riak_host,
            port=options.riak_http_port
        )

        # Riak HTTP client
        self.riak_http_client = riak.RiakClient(
            host=options.riak_host,
            port=options.riak_http_port,
            transport_class=riak.RiakHttpTransport
        )

        # Riak PBC client
        #noinspection PyTypeChecker
        self.riak_pb_client = riak.RiakClient(
            host=options.riak_host,
            port=options.riak_pb_port,
            transport_class=riak.RiakPbcTransport
        )

        # This is a shortcut to quickly switch between the Riak HTTP and PBC client.
        self.client = self.riak_pb_client
        #        self.client = self.riak_http_client

    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", '*')
        self.set_header("Access-Control-Allow-Methods", "GET,PUT,POST,DELETE,OPTIONS")
        self.set_header("Access-Control-Allow-Headers", "Content-Type, Depth, User-Agent, X-File-Size, "
                                                        "X-Requested-With, X-Requested-By, If-Modified-Since, "
                                                        "X-File-Name, Cache-Control, X-Api-Key")

    def options(self, *args, **kwargs):
        """
            Returning back the list of supported HTTP methods
        """
        self.set_status(200)
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Methods", ', '.join([str(x) for x in self.SUPPORTED_METHODS]))
        self.write("ok")

    def respond(self, payload, status_code=200, status_message='OK'):
        """
            The general responder for ALL cases (success response, error response)
        """
        if payload is None:
            payload = {}

        if type(payload) not in [dict, list]:
            logging.error('payload is: {}'.format(payload))
            logging.error('payload is type: {}'.format(type(payload)))
            raise NoDictionaryException()

        response = Response(
            status_code=status_code,
            status_message=status_message,
            result=payload
        ).get_data()

        self.set_status(status_code)
        self.set_header("X-Calvin", "You know, Hobbes, some days even my lucky rocketship underpants don’t help.")
        self.set_header("Content-Type", "application/json; charset=UTF-8")
        self.write(response)
        if status_code in [200, 201, 204, 300]:
            self.finish()

    def write_error(self, status_code, **kwargs):
        """
            Called automatically when an error occurred. But can also be used to
            respond back to caller with a manual error.
        """
        if 'exc_info' in kwargs:
            logging.error(repr(kwargs['exc_info']))

        message = 'Something went seriously wrong! Maybe invalid resource? Ask your admin for advice!'
        if 'message' in kwargs:
            message = kwargs['message']

        self.respond(
            status_code=status_code,
            status_message=message,
            payload={"incident_time": get_current_time_formatted()}
        )
