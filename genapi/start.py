# -*- coding: utf-8 -*-
"""

    GenAPI

    Start GenAPI:

    $ python ./start.py --port=7000 --riak_host=localhost --api_version=1 \
      --api_id=aaaaaaaa --entity=user,object,contact


    Copyright (c) 2012 apitrary

"""
import logging
import os
import sys
import tornado.ioloop
import tornado.web
import tornado.httpserver
import tornado.httputil
import tornado.httpclient
from tornado.options import options
from tornado.options import define
from tornado.options import enable_pretty_logging
from Helpers import show_all_settings, get_bucket_name
from base_handlers import AppStatusHandler, RootWelcomeHandler, SchemaHandler
from config import APP_SETTINGS
from entity_handlers import SimpleEntityHandler
from pre_hooks import pre_start_hook


##############################################################################
#
# GENERAL CONFIGURATION + SHELL PARAMETER DEFINITIONS
#
##############################################################################

# Required shell parameters
define("port", help="run on the given port", type=int)
define("riak_host", help="Riak database host", type=str)
define("api_version", help="API Version (/vXXX)", type=int)
define("api_id", help="Unique API ID", type=str)
define("entity", help="Entity name", type=str, multiple=True)

# Shell parameters with default values
define("config", help="genapi service config file", type=str)
define("env", default='dev', help='start server in test, dev or live mode', type=str)
define("riak_pb_port", default=8087, help="Riak Protocol Buffer port", type=int)
define("riak_http_port", default=8098, help="Riak HTTP port", type=int)
define("riak_rq", default=2, help="Riak READ QUORUM", type=int)
define("riak_wq", default=2, help="Riak WRITE QUORUM", type=int)

# API-specific settings
API_VERSION = options.api_version
API_ID = options.api_id
PORT = options.port

# Enable pretty logging
enable_pretty_logging()


##############################################################################
#
# FUNCTIONS
#
##############################################################################


def routes(parsed_opts):
    """
        Setup the URL routes with regex
    """
    assert parsed_opts.api_version
    assert parsed_opts.api_id
    assert parsed_opts.entity
    assert parsed_opts.riak_rq
    assert parsed_opts.riak_wq

    # This is the prefix for ALL URLs, e.g. /aaaaaaa/v1/user
    base_url = parsed_opts.api_id

    all_routes = [
        (r"/", RootWelcomeHandler),
        (r"/info", RootWelcomeHandler),
        (r"/status", AppStatusHandler, dict(api_version=parsed_opts.api_version, api_id=parsed_opts.api_id)),
        (r"/{}/v{}/schema".format(base_url, parsed_opts.api_version), SchemaHandler, dict(schema=parsed_opts.entity))
    ]

    # Now, go through the list of entities and add routes for each entity.
    for entity in parsed_opts.entity:
        bucket_name = get_bucket_name(parsed_opts.api_id, entity)

        options_dict = dict(
            bucket_name=bucket_name,
            riak_rq=parsed_opts.riak_rq,
            riak_wq=parsed_opts.riak_wq,
            api_id=parsed_opts.api_id,
            api_version=parsed_opts.api_version,
            entity_name=entity
        )

        # Setup route for retrieving all objects
        all_routes.append((
            r"/{}/v{}/{}".format(base_url, parsed_opts.api_version, entity),
            SimpleEntityHandler,
            options_dict
            )
        )

        # Setup route for getting single objects with given id
        all_routes.append((
            r"/{}/v{}/{}/([0-9a-zA-Z]+)".format(base_url, parsed_opts.api_version, entity),
            SimpleEntityHandler,
            options_dict
            )
        )

    return all_routes


def options_ok(parsed_opts):
    """
        Check if all options passed on as parameters are ok!
    """
    ok = True

    if parsed_opts.port is None:
        ok = False
        logging.error('Missing attribute: --port')

    if parsed_opts.riak_host is None:
        ok = False
        logging.error('Missing attribute: --riak_host')

    if parsed_opts.api_id is None:
        ok = False
        logging.error('Missing attribute: --api_id')

    if parsed_opts.api_version is None:
        ok = False
        logging.error('Missing attribute: --api_version')

    if parsed_opts.entity is None or len(parsed_opts.entity) == 0:
        ok = False
        logging.error('Missing attribute: --entity')

    if not ok:
        print("[ERROR] Errors found!")
        print("")
        print("Use --help to see the help page.")

    return ok


def _start_tornado_server(port, routes_configuration):
    """
        Start the Tornado server
    """
    # Setup the application context
    application = tornado.web.Application(
        handlers=routes_configuration,
        **APP_SETTINGS
    )

    # Setup the HTTP server
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(port)

    # Ok, we're ready to start!
    tornado.ioloop.IOLoop.instance().start()


def start_server(parsed_opts):
    """
        Start the general server
    """
    # Get all established routes
    routes_configuration = routes(parsed_opts)

    # Show all configured handlers
    show_all_settings(parsed_opts, routes_configuration)

    # Start the API
    assert parsed_opts.port
    _start_tornado_server(parsed_opts.port, routes_configuration)


def main():
    """
        Run all steps and config checks, then start the server
    """
    ok = True

    if options.config:
        if os.path.exists(options.config):
            tornado.options.parse_config_file(options.config)
        else:
            logging.warn('Config file {} not found! Skipping.'.format(options.config))
    else:
        logging.info("No configuration file provided! Parsing shell parameters.")

        try:
            # Parse the command line options
            tornado.options.parse_command_line()
        except tornado.options.Error, e:
            sys.exit('ERROR: {}'.format(e))

        # From now on, we have the "parsed_opts" object.
        # Ok, go & check the required options.
        ok = options_ok(options)

    if ok:
        # Run the PRE-START hooks
        pre_start_hook(parsed_opts=options)

        # Start the server
        start_server(parsed_opts=options)

##############################################################################
#
# MAIN
#
##############################################################################

if __name__ == "__main__":
    main()
