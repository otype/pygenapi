# -*- coding: utf-8 -*-
"""

    GenAPI

    Copyright (c) 2012 apitrary

"""
import json
import logging
import uuid
import os
import riak
import time
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
# GENERAL CONFIGURATION + SHELL PARAMETER DEFINITIONS
#
##############################################################################

# Shell options from Tornado
define("config", default='genapi.conf', help="genapi service config file", type=str)
define("port", default=7000, help="run on the given port", type=int)
#define("env", default='dev', help='start server in test, dev or live mode', type=str)
define("riak_host", default="localhost", help="Riak database host", type=str)
define("riak_http_port", default=8098, help="Riak HTTP port", type=int)
define("riak_pb_port", default=8087, help="Riak Protocol Buffer port", type=int)
define("riak_rq", default=2, help="Riak READ QUORUM", type=int)
define("riak_wq", default=2, help="Riak WRITE QUORUM", type=int)
define("riak_bucket_name", default='genapi_object', help="Riak bucket name", type=str)
define("api_version", default=1, help="API Version (/vXXX)", type=int)
define("api_id", default='aaaaaaaaaa_1', help="Unique API ID", type=str)

# API-specific settings
API_VERSION = options.api_version
API_ID = options.api_id

# API version URL
api_version_url = '/v{}'.format(API_VERSION)

# Enable pretty logging
enable_pretty_logging()

# Application details
APP_DETAILS = {
    'name': 'GenAPI v1',
    'version': '0.1',
    'company': 'apitrary',
    'support': 'http://apitrary.com/support',
    'contact': 'support@apitrary.com',
    'copyright': '2012 apitrary.com',
    'API version': API_VERSION,
    'id': API_ID
}

# Cookie secret
COOKIE_SECRET = 'Pa1eevenie-di4koGheiKe7ki_inoo2quiu0Xohhaquei4thuv'

# General app settings for Tornado
APP_SETTINGS = {
    'cookie_secret': COOKIE_SECRET,
    'xheaders': True
}

##############################################################################
#
# HANDLERS
#
##############################################################################


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

    def write_error(self, status_code, **kwargs):
        """
            Called automatically when an error occurred. But can also be used to
            respond back to caller with a manual error.
        """
        if kwargs.has_key('exc_info'):
            logging.error(repr(kwargs['exc_info']))

        message = 'Something went seriously wrong! Maybe invalid resource? Ask your admin for advice!'
        if kwargs.has_key('message'):
            message = kwargs['message']

        self.set_status(status_code)
        self.write({
            'error': message,
            'incident_time': time.time()
        })


class RootWelcomeHandler(BaseHandler):
    """
        GET '/'
    """

    def get(self, *args, **kwargs):
        """
            Print out the welcome message. Should be available at '/'.
        """
        self.write(
                {'message': 'Welcome to apitrary\'s {} API v.{}!'.format(APP_DETAILS['name'], APP_DETAILS['version'])}
        )


class AppInfoHandler(BaseHandler):
    """
        GET '/info'
        GET '/info/'
    """

    def get(self, *args, **kwargs):
        """
            Print out the application details (see APP_DETAILS)
        """
        self.write(APP_DETAILS)


class DatabaseAliveHandler(BaseHandler):
    """
        GET '/dbping'
        GET '/dbping/'
    """

    @tornado.web.asynchronous
    @tornado.gen.engine
    def get(self, *args, **kwargs):
        """
            Asynchronously checks the database status by calling Riak's /ping url.
        """
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
        """
            Asynchronously calls the Riak stats.
        """
        riak_stats_url = '{}/stats'.format(self.riak_url)
        response = yield tornado.gen.Task(self.async_http_client.fetch, riak_stats_url)
        self.write(response.body)
        self.finish()


class MultipleObjectHandler(BaseHandler):
    """
        GET '/objects'
        GET '/objects?q=<key>:<search_value>'

        Multiple object Key-/Value-pair handler. Used for the first iteration of apitrary.
    """

    # Set of supported methods for this resource
    SUPPORTED_METHODS = ("GET")

    def __init__(self, application, request, **kwargs):
        """
            Sets up the Riak client and the bucket
        """
        super(MultipleObjectHandler, self).__init__(application, request, **kwargs)
        self.bucket_name = options.riak_bucket_name
        logging.debug('Setting bucket = {}'.format(self.bucket_name))

        # Setup the Riak bucket
        self.bucket = self.client.bucket(self.bucket_name).set_r(options.riak_rq).set_w(options.riak_wq)

    def fetch_all(self):
        query = riak.RiakMapReduce(self.client).add(self.bucket_name)
        query.map('function(v) { var data = JSON.parse(v.values[0].data); return [[v.key, data]]; }')
        return query.run()

    def search(self, question):
        query = self.client.search(self.bucket_name, question)
        logging.debug('search_query: {}'.format(query))
        response = []
        for result in query.run():
            # Getting ``RiakLink`` objects back.
            obj = result.get()
            obj_data = obj.get_data()
            response.append(obj_data)

        return response

    #noinspection PyMethodOverriding
    def get(self):
        """
            Fetch a set of objects. If user doesn't provide a query (e.g. place:Hann*), then
            we assume the user wants to have all objects in this bucket.
        """
        # TODO: Add another way to limit the query results (fetch_all()[:100])
        # TODO: Add another way to query for documents after/before a certain date

        query = self.get_argument('q', default=None)

        results = ''
        try:
            if query:
                results = self.search(query)
            else:
                results = self.fetch_all()
        except Exception, e:
            logging.error(e)
            self.write_error(500, message='Error on fetching all objects!')

        self.write({'results' : results})

class SingleObjectHandler(BaseHandler):
    """
        GET '/object'
        POST '/object'
        PUT '/object'
        DELETE '/object'

        Single object Key-/Value-pair handler. Used for the first iteration of apitrary.
    """

    # Set of supported methods for this resource
    SUPPORTED_METHODS = ("GET", "POST", "PUT", "DELETE")

    def __init__(self, application, request, **kwargs):
        """
            Sets up the Riak client and the bucket
        """
        super(SingleObjectHandler, self).__init__(application, request, **kwargs)
        bucket_name = options.riak_bucket_name
        logging.debug('Setting bucket = {}'.format(bucket_name))

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
        logging.debug("created new object id: {}".format(object_id))
        try:
            obj_to_store = json.loads(unicode(self.request.body, 'latin-1'))
            if obj_to_store is None:
                raise tornado.web.HTTPError(403)

            # Check if this post is valid
            obj_to_store['created_at'] = time.time()
            obj_to_store['updated_at'] = time.time()
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
            logging.debug("Deleted object with id: {}".format(object_id))
            self.set_status(200)
            self.write({"deleted": object_id})
        else:
            raise tornado.web.HTTPError(403, log_message='Could not delete object with id: {}'.format(object_id))

##############################################################################
#
# ROUTING CONFIGURATION
#
##############################################################################

# All routes to handle within this API
handlers = [
    (r"{}/".format(api_version_url), RootWelcomeHandler),
    (r"{}/info".format(api_version_url), AppInfoHandler),
    (r"{}/info/".format(api_version_url), AppInfoHandler),
    (r"{}/dbping".format(api_version_url), DatabaseAliveHandler),
    (r"{}/dbping/".format(api_version_url), DatabaseAliveHandler),
    (r"{}/dbstats".format(api_version_url), DatabaseStatusHandler),
    (r"{}/dbstats/".format(api_version_url), DatabaseStatusHandler),
    (r"{}/objects".format(api_version_url), MultipleObjectHandler),
    (r"{}/objects/".format(api_version_url), MultipleObjectHandler),
    (r"{}/object".format(api_version_url), SingleObjectHandler),
    (r"{}/object/".format(api_version_url), SingleObjectHandler),
    (r"{}/object/([0-9a-zA-Z]+)".format(api_version_url), SingleObjectHandler)
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