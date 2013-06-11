# -*- coding: utf-8 -*-
"""

    GenAPI

    Copyright (c) 2012 - 2013 apitrary

"""
import tornado
import tornado.web
from tornado import gen
from settings.config import APP_DETAILS
from simple_entity.base_handlers import BaseHandler


class ApiStatusHandler(BaseHandler):
    """
        GET '/'
        Shows status information about this about this deployed API
    """

    def __init__(self, application, request, api_version, api_id, schema, api_key, **kwargs):
        """
            Set up the basic Api Status handler responding on '/'
        """
        super(ApiStatusHandler, self).__init__(application, request, **kwargs)
        self.api_version = api_version
        self.api_id = api_id
        self.schema = schema
        self.api_key = api_key

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
