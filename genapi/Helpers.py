# -*- coding: utf-8 -*-
"""

    GenAPI

    Copyright (c) 2012 apitrary

"""
import logging

def get_bucket_name(api_id, entity_name):
    """
        To create uniform bucket names
    """
    return '{}_{}'.format(api_id, entity_name)


def show_all_settings(opts, routes_configuration):
    """
        Show all routes configured for this service
    """
    assert opts.logging
    assert opts.port
    assert opts.riak_host
    assert opts.api_id
    assert opts.api_version

    logging.info('LOGGING LEVEL: {}'.format(opts.logging))
    logging.info('SERVER PORT: {}'.format(opts.port))
    logging.info('RIAK HOST: {}'.format(opts.riak_host))
    logging.info('ENTITIES: {}'.format(opts.entity))
    logging.info('API ID: {}'.format(opts.api_id))
    logging.info('API VERSION: {}'.format(opts.api_version))
    for route in routes_configuration:
        logging.info('NEW ROUTE: {} -- Handled by: "{}"'.format(repr(route[0]), route[1]))
