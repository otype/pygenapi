# -*- coding: utf-8 -*-
"""

    GenAPI

    Copyright (c) 2012 apitrary

"""
import json
import logging
import socket
import riak
import sys
import tornado
import tornado.ioloop
from _socket import gaierror
from tornado.httpclient import AsyncHTTPClient
from genapi.support import get_bucket_name, database_bucket_url


def store_init_object(opts, entity_name):
    assert opts.riak_host
    assert opts.api_id
    assert opts.riak_http_port
    assert opts.riak_rq
    assert opts.riak_wq

    # Riak HTTP client
    client = riak.RiakClient(
        host=opts.riak_host,
        port=opts.riak_http_port,
        transport_class=riak.RiakHttpTransport
    )

    # setup the bucket
    bucket_name = get_bucket_name(opts.api_id, entity_name)
    bucket = client.bucket(bucket_name).set_r(opts.riak_rq).set_w(opts.riak_wq)

    init_object = {'_init': 'OK'}
    logging.debug('Initializing bucket: "{}" with object: "{}"'.format(bucket_name, init_object))

    try:
        # now, write the init object to the bucket
        bucket.new('_init', init_object).store()
    except riak.RiakError, e:
        logging.error('Error on communicating to Riak database! {}'.format(e))
        tornado.ioloop.IOLoop.instance().stop()
        sys.exit(1)
    except gaierror, e:
        logging.error('Cannot connect to Riak database! Error: {}'.format(e))
        tornado.ioloop.IOLoop.instance().stop()
        sys.exit(1)
    except socket.error, e:
        logging.error('Cannot connect to Riak database! Error: {}'.format(e))
        tornado.ioloop.IOLoop.instance().stop()
        sys.exit(1)


def curl_http_client():
    """
        Configure HTTPClient to use curl_httpclient. Though, this requires pycurl.
    """
    AsyncHTTPClient.configure("tornado.curl_httpclient.CurlAsyncHTTPClient")
    return tornado.httpclient.HTTPClient()


def precommit_hook_exists(riak_bucket_url):
    """
        Asks Riak on given bucket URL for the properties; will check in the
        properties if the precommit hook for SOLR indexing has been set.

        Check basho's documentation for more information:
        http://wiki.basho.com/Riak-Search---Indexing-and-Querying-Riak-KV-Data.html#Setting-up-Indexing
    """
    # We're assuming, as default, that the hook has not been installed
    hook_exists = False

    # contact Riak and fetch the props
    resp = curl_http_client().fetch(
        riak_bucket_url,
        method='GET',
        headers={'content-type': 'application/json', 'accept': 'application/json'}
    )

    # convert the response to json
    json_object = json.loads(resp.body)
    logging.debug(json_object)
    if json_object['props']:
        if json_object['props']['precommit']:
            for hook in json_object['props']['precommit']:
                # Check for {'mod': 'riak_search_kv_hook', 'fun': 'precommit'}
                if hook['mod']:
                    if hook['mod'] == 'riak_search_kv_hook':
                        logging.debug("Precommit hook 'riak_search_kv_hook' already exists!")
                        hook_exists = True

    return hook_exists


def precommit_hook():
    """
        Send this hash to Riak to establish the SOLR indexing.

        Check basho's documentation for more information:
        http://wiki.basho.com/Riak-Search---Indexing-and-Querying-Riak-KV-Data.html#Setting-up-Indexing

        The hash has to be a single string, otherwise the http client will mess up things.
    """
    return '{"props": {"precommit": [{"mod": "riak_search_kv_hook", "fun": "precommit"}]}}'


def send_precommit_hook(riak_bucket_url):
    """
        Sends the actual PUT request for establishing the precommit hook.

        Check basho's documentation for more information:
        http://wiki.basho.com/Riak-Search---Indexing-and-Querying-Riak-KV-Data.html#Setting-up-Indexing
    """
    logging.debug("Setting up precommit hook for indexing.")
    curl_http_client().fetch(
        riak_bucket_url,
        method='PUT',
        headers={'content-type': 'application/json', 'accept': 'application/json'},
        body=precommit_hook()
    )


def setup_indexing(opts, entity_name):
    """
        This will setup the PRECOMMIT hook for indexing (SOLR) in Riak
        for a given entity.
    """
    # Construct the bucket name
    bucket_name = get_bucket_name(opts.api_id, entity_name)

    # and now, the complete Riak bucket URL
    riak_bucket_url = database_bucket_url(db_host=opts.riak_host, db_port=opts.riak_http_port, bucket_name=bucket_name)

    # Ask if the hook is already setup
    hook = precommit_hook_exists(riak_bucket_url=riak_bucket_url)

    # If it's not, then setup the hook
    if not hook:
        logging.debug("Precommit hook not established! Trying to set it up!")
        send_precommit_hook(riak_bucket_url=riak_bucket_url)
    else:
        logging.debug('Hook already initialized! Skipping hook setup.')


def initialize_buckets(opts):
    """
        Does two things:
            1. create the bucket by storing a simple object in there
            2. sets up the SOLR indexing by posting a magic JSON object
    """
    assert opts.entity

    for entity in opts.entity:
        logging.debug('Setting up bucket for entity: {}'.format(entity))

        # First, store the init object (and, implicitly, create the bucket)
        store_init_object(opts=opts, entity_name=entity)

        # Second, setup the indexing
        setup_indexing(opts=opts, entity_name=entity)

##############################################################################
#
# HOOK
#
##############################################################################


def pre_start_hook(parsed_opts):
    """
        The PRE-Start hook! Before starting the server, actions can be run.
    """

    # Initialize all buckets
    initialize_buckets(opts=parsed_opts)
