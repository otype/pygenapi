# -*- coding: utf-8 -*-
"""

    GenAPI

    Copyright (c) 2012 apitrary

"""
from datetime import datetime
import json
import logging
import uuid
import os
import riak
import tornado.ioloop
import tornado.web
from tornado import httpclient
from tornado import gen
import tornado.httpserver
import tornado.httputil
from tornado.options import options
from tornado.options import define
from tornado.options import enable_pretty_logging

##############################################################################
#
# GENERAL CONFIGURATION
#
##############################################################################


APP_DETAILS = {
    'name': 'GenAPI v1',
    'version': '0.1',
    'company': 'apitrary',
    'support': 'http://apitrary.com/support',
    'contact': 'support@apitrary.com',
    'copyright': '2012 apitrary.com'
}

# Cookie secret
COOKIE_SECRET = 'Pa1eevenie-di4koGheiKe7ki_inoo2quiu0Xohhaquei4thuv'

# General app settings for Tornado
APP_SETTINGS = {
    'cookie_secret': COOKIE_SECRET,
    'xheaders': True
}

# Increment this version
API_VERSION = 1

##############################################################################
#
# HANDLERS
#
##############################################################################


class BaseHandler(tornado.web.RequestHandler):
    def __init__(self, application, request, **kwargs):
        """
            Base initializer! Sets up the riak (sync) client and the async http client for async Riak calls.
        """
        super(BaseHandler, self).__init__(application, request, **kwargs)

        # Setup the Async HTTP client for calling Riak asynchronously
        self.async_http_client = tornado.httpclient.AsyncHTTPClient()

        # Setup Riak URLs for AsyncHttpClient
        self.riak_protocol = 'http://'
        self.riak_url = '{protocol}{node}:{port}'.format(
            protocol=self.riak_protocol,
            node=options.riak_host,
            port=options.riak_port
        )


    def write_error(self, status_code, **kwargs):
        """
            Called automatically when an error occurred.
        """
        if kwargs.has_key('exc_info'):
            logging.error(repr(kwargs['exc_info']))

        message = 'Something went seriously wrong! Maybe invalid resource? Ask your admin for advice!'
        if kwargs.has_key('message'):
            message = kwargs['message']

        self.set_status(status_code)
        self.write({
            'error': message,
            'incident_time': datetime.utcnow().isoformat()
        })


class RootWelcomeHandler(BaseHandler):
    """
        GET '/'
    """

    def get(self, *args, **kwargs):
        self.write(
                {'message': 'Welcome to apitrary\'s {} API v.{}!'.format(APP_DETAILS['name'], APP_DETAILS['version'])}
        )


class AppInfoHandler(BaseHandler):
    """
        GET '/info'
        GET '/info/'
    """

    def get(self, *args, **kwargs):
        self.write(APP_DETAILS)


class DatabaseAliveHandler(BaseHandler):
    """
        GET '/dbping'
        GET '/dbping/'
    """

    @tornado.web.asynchronous
    @tornado.gen.engine
    def get(self, *args, **kwargs):
        riak_ping_url = '{}/ping'.format(self.riak_url)
        response = yield tornado.gen.Task(self.async_http_client.fetch, riak_ping_url)
        self.write({'ping': response.body})
        self.finish()


class DatabaseStatusHandler(BaseHandler):
    """
        GET '/dbstats'
        GET '/dbstats/'
    """

    @tornado.web.asynchronous
    @tornado.gen.engine
    def get(self, *args, **kwargs):
        riak_stats_url = '{}/stats'.format(self.riak_url)
        response = yield tornado.gen.Task(self.async_http_client.fetch, riak_stats_url)
        self.write(response.body)
        self.finish()


class GenericKeyValueHandler(BaseHandler):
    """
        Generic Key-/Value-pair handler
    """
    # Set of supported methods for this resource
    SUPPORTED_METHODS = ("GET", "POST", "PUT", "DELETE")

    def __init__(self, application, request, **kwargs):
        """
            Sets up the Riak client and the bucket
        """
        super(GenericKeyValueHandler, self).__init__(application, request, **kwargs)
        bucket_name = '{}_{}'.format(options.riak_bucket_name, options.env)
        logging.info('Setting bucket = {}'.format(bucket_name))

        # Setup Riak client
        self.client = riak.RiakClient(
            host=options.riak_host,
            port=options.riak_port,
            transport_class=riak.RiakHttpTransport
        )

        # Setup the Riak bucket
        self.bucket = self.client.bucket(bucket_name).set_r(options.riak_rq).set_w(options.riak_wq)

    def get(self, object_id):
        """
            Retrieve blog post with given id
        """
        if object_id is None:
            raise tornado.web.HTTPError(403)

        self.write(self.bucket.get(object_id).get_data())

    def post(self, *args, **kwargs):
        """
            Stores a new blog post into Riak
        """
        object_id = uuid.uuid1().hex
        logging.info("created new object id: {}".format(object_id))
        try:
            obj_to_store = json.loads(unicode(self.request.body, 'latin-1'))
            if obj_to_store is None:
                raise tornado.web.HTTPError(403)

            # Check if this post is valid
            obj_to_store['created_at'] = datetime.utcnow().toordinal()
            obj_to_store['updated_at'] = datetime.utcnow().toordinal()
            result = self.bucket.new(object_id, obj_to_store).store()
            self.write({"id": result._key})
        except ValueError:
            self.write_error(500, message='Cannot store object!')
        except Exception, e:
            self.write_error(500, message=e.value)

    def put(self, object_id=None):
        """
            Stores a new blog post into Riak
        """
        if object_id is None:
            raise tornado.web.HTTPError(403, log_message="Missing object id")

        try:
            obj_to_store = json.loads(unicode(self.request.body, 'latin-1'))
            if obj_to_store is None:
                raise tornado.web.HTTPError(
                    403,
                    log_message='Updating object with id: {} not possible.'.format(object_id)
                )

            # Check if this post is valid
            updated_object = self.bucket.new(object_id, data=obj_to_store).store()
            self.write({"id": updated_object._key})
        except ValueError:
            self.write_error(500, message='Cannot store object!')
        except Exception, e:
            self.write_error(500, message=e.value)

    def delete(self, object_id=None):
        """
            Stores a new blog post into Riak
        """
        if object_id is None:
            raise tornado.web.HTTPError(403, log_message="Missing object id")

        object_to_store = self.bucket.get(object_id)
        if object_to_store.get_data() is None:
            raise tornado.web.HTTPError(403, log_message='Object with id: {} does not exist.'.format(object_id))

        result = object_to_store.delete()
        if result.get_data() is None:
            logging.info("Deleted object with id: {}".format(object_id))
            self.set_status(200)
            self.write({"deleted": object_id})
        else:
            raise tornado.web.HTTPError(403, log_message='Could not delete object with id: {}'.format(object_id))

##############################################################################
#
# SHELL CONFIGURATION PARAMETERS
#
##############################################################################

# Shell options
define("config", default='genapi.conf', help="genapi service config file", type=str)
define("port", default=6000, help="run on the given port", type=int)
define("env", default='dev', help='start server in test, dev or live mode', type=str)
define("riak_host", default="localhost", help="Riak database host", type=str)
define("riak_port", default=8098, help="Riak database port", type=int)
define("riak_rq", default=2, help="Riak READ QUORUM", type=int)
define("riak_wq", default=2, help="Riak WRITE QUORUM", type=int)
define("riak_bucket_name", default='genapiv1_somerandomname', help="Riak bucket name", type=str)

# API version URL
api_version_url = '/v{}'.format(API_VERSION)

# Enable pretty logging
enable_pretty_logging()

# All routes to handle within this API
handlers = [
    (r"{}/".format(api_version_url), RootWelcomeHandler),
    (r"{}/info".format(api_version_url), AppInfoHandler),
    (r"{}/info/".format(api_version_url), AppInfoHandler),
    (r"{}/dbping".format(api_version_url), DatabaseAliveHandler),
    (r"{}/dbping/".format(api_version_url), DatabaseAliveHandler),
    (r"{}/dbstats".format(api_version_url), DatabaseStatusHandler),
    (r"{}/dbstats/".format(api_version_url), DatabaseStatusHandler),
    (r"{}/object".format(api_version_url), GenericKeyValueHandler),
    (r"{}/object/".format(api_version_url), GenericKeyValueHandler),
    (r"{}/object/([0-9a-zA-Z]+)".format(api_version_url), GenericKeyValueHandler)
]

# Start the tornado application
application = tornado.web.Application(
    handlers=handlers,
    **APP_SETTINGS
)

##############################################################################
#
# FUNCTIONS
#
##############################################################################

def show_all_settings():
    """
        Show all routes configured for this service
    """
    logging.info('SERVER PORT: {}'.format(options.port))
    for route in handlers:
        logging.info('NEW ROUTE: {} -- Handled by: "{}"'.format(repr(route[0]), route[1]))


def main():
    """
        Start the Tornado Web server
    """
    # Parse the command line options
    if os.path.exists(options.config):
        tornado.options.parse_config_file(options.config)
    else:
        tornado.options.parse_command_line()

    # Setup the HTTP server
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(options.port)

    # Show all configured handlers
    show_all_settings()

    # Ok, we're ready to start!
    tornado.ioloop.IOLoop.instance().start()


##############################################################################
#
# MAIN
#
##############################################################################

if __name__ == "__main__":
    main()