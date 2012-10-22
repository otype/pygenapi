# -*- coding: utf-8 -*-
"""

    GenAPI

    Copyright (c) 2012 apitrary

"""
import logging
import riak
import time
import tornado.ioloop
import tornado.web
import tornado.escape
from tornado import httpclient
from tornado import gen
import tornado.httpserver
import tornado.httputil
from tornado.options import options
from config import APP_DETAILS
from response import Response


class BaseHandler(tornado.web.RequestHandler):
    """
        The most general handler class. Should be sub-classed by all consecutive
        handler classes.
    """

    def __init__(self, application, request, **kwargs):
        """
            Base initializer! Sets up the riak (sync) client and the async http client for async Riak calls.
        """
        super(BaseHandler, self).__init__(application, request, **kwargs)

        # Setup the Async HTTP client for calling Riak asynchronously
        self.async_http_client = tornado.httpclient.AsyncHTTPClient()

        # Setup Riak base URLs for AsyncHttpClient
        # TODO: Make this configurable from outside the PyGenAPI!
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
                                                        "X-File-Name, Cache-Control")

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

        self.set_status(status_code)
        self.write(
            Response(
                status_code=status_code,
                status_message=message,
                result={"incident_time": time.time()}
            ).get_data()
        )
        self.finish()


class ApiStatusHandler(BaseHandler):
    """
        GET '/'
        Shows status information about this about this deployed API
    """

    def __init__(self, application, request, api_version, api_id, schema, **kwargs):
        """
            Set up the basic Api Status handler responding on '/'
        """
        super(ApiStatusHandler, self).__init__(application, request, **kwargs)
        self.api_version = api_version
        self.api_id = api_id
        self.schema = schema

    @tornado.web.asynchronous
    @tornado.gen.engine
    def get(self, *args, **kwargs):
        """
            Provides a basic hash with information for this deployed API.
        """
        # create status
        riak_ping_url = '{}/ping'.format(self.riak_url)
        response = yield tornado.gen.Task(self.async_http_client.fetch, riak_ping_url)
        riak_db_status = response.body

        status = {
            'db_status': riak_db_status,
            'api': {
                'api_version': self.api_version,
                'api_id': self.api_id
            }
        }

        # create the output
        application_status = {
            'info': APP_DETAILS,
            'status': status,
            'schema': self.schema
        }

        self.write(application_status)
        self.finish()
