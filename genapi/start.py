# -*- coding: utf-8 -*-
"""

    GenAPI

    Copyright (c) 2012 apitrary

"""
import logging
import os
import tornado.ioloop
import tornado.web
import tornado.httpserver
import tornado.httputil
from tornado.options import options
from tornado.options import define
from tornado.options import enable_pretty_logging
from base_handlers import AppStatusHandler, RootWelcomeHandler
from config import APP_SETTINGS
from entity_handlers import MultipleObjectHandler, SingleObjectHandler


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
API_VERSION_URL = '/v{}'.format(API_VERSION)

# Enable pretty logging
enable_pretty_logging()

##############################################################################
#
# ROUTING CONFIGURATION
#
##############################################################################

# All routes to handle within this API
ROUTES = [
    (r"/", RootWelcomeHandler),
    (r"/info", RootWelcomeHandler),
    (r"/status", AppStatusHandler, dict(api_version=API_VERSION)),
    (r"{}/objects".format(API_VERSION_URL), MultipleObjectHandler),
    (r"{}/object".format(API_VERSION_URL), SingleObjectHandler),
    (r"{}/object/([0-9a-zA-Z]+)".format(API_VERSION_URL), SingleObjectHandler)
]

# Start the tornado application
application = tornado.web.Application(
    handlers=ROUTES,
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
    logging.info('RIAK HOST: {}'.format(options.riak_host))
    logging.info('RIAK HTTP PORT: {}'.format(options.riak_http_port))
    logging.info('RIAK PBC PORT: {}'.format(options.riak_pb_port))
    for route in ROUTES:
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