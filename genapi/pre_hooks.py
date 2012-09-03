# -*- coding: utf-8 -*-
"""

    GenAPI

    Copyright (c) 2012 apitrary

"""
import json
import logging
import urllib
import riak
import sys
import tornado
from tornado.httpclient import AsyncHTTPClient
from Helpers import get_bucket_name

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

    # now, write the init object to the bucket
    bucket.new('_init', init_object).store()


def setup_indexing(opts, entity_name):
    """
        This one is a bit complicated:
            1. Setup the Riak URL we need (e.g. http://localhost:8098/riak/<bucket_name>
            2. Fetch the props from this bucket
            3. Check if we already have the INDEX SOLR precommit hook set
                NO: Run a PUT request with the necessary precommit hook
                YES: Skip the PUT request
    """
    # Ok, now setup the indexing by posting the magic json object!
    riak_protocol = 'http://'
    riak_base_url = '{protocol}{node}:{port}'.format(
        protocol=riak_protocol,
        node=opts.riak_host,
        port=opts.riak_http_port
    )

    # Construct the bucket url, e.g. http://localhost:8098/riak/<bucket_name>
    bucket_name = get_bucket_name(opts.api_id, entity_name)
    riak_url = "{}/riak/{}".format(riak_base_url, bucket_name)
    logging.debug("INDEXING INIT: {}".format(riak_url))

    # Following is taken from basho's documentation:
    # http://wiki.basho.com/Riak-Search---Indexing-and-Querying-Riak-KV-Data.html#Setting-up-Indexing
    body_data = {'props': {'precommit': [{'mod': 'riak_search_kv_hook', 'fun': 'precommit'}]}}
    body = urllib.urlencode(body_data)
    header = {'content-type': 'application/json', 'accept':'application/json'}

    # Now, send the data as POST request to the bucket via tornado's HTTP client
    AsyncHTTPClient.configure("tornado.curl_httpclient.CurlAsyncHTTPClient")
    http_client = tornado.httpclient.HTTPClient()

    try:
        # Get the current props
        resp = http_client.fetch(riak_url, method='GET', headers=header)

        # check if the props have the precommit hook
        json_object = json.loads(resp.body)
        logging.debug(json_object)
        if json_object['props']['precommit'] and len(json_object['props']['precommit']) < 1:
            # They don't! Ok, then PUT the precommit hook
            logging.debug("Setting up index hook")
            http_client.fetch(riak_url, method='PUT', headers=header, body=body)
    except tornado.httpclient.HTTPError, e:
        logging.error(e)
        sys.exit(e)


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


