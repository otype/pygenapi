# -*- coding: utf-8 -*-
"""

    GenAPI

    Copyright (c) 2012 apitrary

"""
import logging
import random
import riak
import tornado.ioloop
import tornado.web
import tornado.escape
from tornado import httpclient
import tornado.httpserver
import tornado.httputil
from tornado.options import options
from errors import NoDictionaryException
from models.error_response import ErrorResponse
from models.response import Response


class BaseHandler(tornado.web.RequestHandler):
    """
        The most general handler class. Should be sub-classed by all consecutive
        handler classes.
    """

    def __init__(self, application, request, **kwargs):
        super(BaseHandler, self).__init__(application, request, **kwargs)

        self.async_http_client = tornado.httpclient.AsyncHTTPClient()
        self.riak_protocol = 'http'
        self.riak_url = '{protocol}://{node}:{port}'.format(
            protocol=self.riak_protocol,
            node=options.riak_host,
            port=options.riak_http_port
        )

        self.riak_http_client = riak.RiakClient(
            host=options.riak_host,
            port=options.riak_http_port,
            transport_class=riak.RiakHttpTransport
        )

        #noinspection PyTypeChecker
        self.riak_pb_client = riak.RiakClient(
            host=options.riak_host,
            port=options.riak_pb_port,
            transport_class=riak.RiakPbcTransport
        )

        # This is a shortcut to quickly switch between the Riak HTTP and PBC client.
        self.client = self.riak_pb_client

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
        self.set_header("X-Calvin", self.calvinQuote())
        self.set_header("Content-Type", "application/json; charset=UTF-8")
        self.write(response)

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

        response = ErrorResponse(error_message=message)

        self.set_status(status_code)
        self.set_header("X-Calvin", self.calvinQuote())
        self.set_header("Content-Type", "application/json; charset=UTF-8")
        self.write(response.get_data())

    def calvinQuote(self):
        return random.choice([
            "You know, Hobbes, some days even my lucky rocketship underpants don’t help.",
            "That is the difference between me and the rest of the world! Happiness isn’t good " +
            "enough for me! I demand euphoria!",
            "In my opinion, we don’t devote nearly enough scientific research to finding a cure for jerks.",
            "What’s the point of wearing your favorite rocketship underpants if nobody ever asks to see ‘em?",
            "This one’s tricky. You have to use imaginary numbers, like eleventeen …",
            "I’m learning real skills that I can apply throughout the rest of my life … Procrastinating " +
            "and rationalizing.",
            "I’m not dumb. I just have a command of thoroughly useless information.",
            "Life’s disappointments are harder to take when you don’t know any swear words.",
            "I like maxims that don’t encourage behavior modification.",
            "Weekends don’t count unless you spend them doing something completely pointless.",
            "A little rudeness and disrespect can elevate a meaningless interaction to a battle of wills and "
            "add drama to an otherwise dull day.",
            "It’s psychosomatic. You need a lobotomy. I’ll get a saw.",
            "I understand my tests are popular reading in the teachers’ lounge.",
            "I go to school, but I never learn what I want to know."
        ])
