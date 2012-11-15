# -*- coding: utf-8 -*-
"""

    GenAPI - Analytics library

    Copyright (c) 2012 apitrary

"""
import logging
import urllib
from tornado import httpclient
from tornado.httpclient import HTTPRequest

def handle_async_request(response):
    """
        Callback for the AsyncHTTPClient call to our Piwik Installation
    """
    if response.error:
        logging.error('Piwik Tracking failed! Error: {}'.format(response.error))
    else:
        logging.debug('Piwik Tracking succeeded.')


def piwik_opts(piwik_site_id, piwik_rec, tracking_url, action_name):
    """
        Construct the Piwik Options hash
    """
    return {
        'idsite': piwik_site_id,
        'rec': piwik_rec,
        'url': tracking_url,
        'action_name': action_name
    }


def get_tracking_url(api_id, api_version, http_method, entity_name, genapi_tracking_host='http://pygenapi'):
    """
        Construct our self-defined tracking url
    """
    return '{}/{}/v{}/{}/{}'.format(genapi_tracking_host, api_id, api_version, http_method, entity_name)


def send_data_asynchronously(piwik_site_id, piwik_rec, piwik_api_url, tracking_url, action_name):
    """
        NOT-BLOCKING (asynchronous) Piwik call
    """
    # Build options hash
    opts = piwik_opts(
        piwik_site_id=piwik_site_id,
        piwik_rec=piwik_rec,
        tracking_url=tracking_url,
        action_name=action_name
    )

    # Create async client
    http_client = httpclient.AsyncHTTPClient()

    # Encode this data and generate request with the final URL
    data = urllib.urlencode(opts)

    # Create the request object with the options hash and the url-encoded API Url + headers
    url = u"%s?%s" % (piwik_api_url, data)
    print url
    http_request = HTTPRequest(
        url=url,
        method='GET',
        headers={'User-Agent': 'genapi analytics-piwik'}
    )

    # Run the call
    http_client.fetch(request=http_request, callback=handle_async_request)
    return True


def get_piwik_api_url(piwik_host):
    """
        Construct the Piwik API Url
    """
    return 'http://{}/piwik/piwik.php'.format(piwik_host)

##############################################################################
#
# Trigger Piwik analytics call
#
##############################################################################


def track_request(piwik_host, piwik_site_id, piwik_rec, api_id, api_version, http_method, entity_name, request=None):
    if request:
        # e.g. extract the request data like user-agent etc.
        pass

    # Get the tracking url for apitrary's genapi
    tracking_url = get_tracking_url(
        api_id=api_id,
        api_version=api_version,
        http_method=http_method,
        entity_name=entity_name
    )

    # Get the Piwik API URL
    piwik_api_url = get_piwik_api_url(piwik_host)

    # send the data asynchronously
    analytics = send_data_asynchronously(
        piwik_site_id=piwik_site_id, # piwik's configured site for genapi
        piwik_rec=piwik_rec, # always set to 1 for persisting logs
        piwik_api_url=piwik_api_url, # Piwik Analytics host name
        tracking_url=tracking_url, # Tracking URL
        action_name=api_id # Identifier for the given API
    )

    return analytics

#if __name__ == "__main__":
#    api_id = 'universalapi'
#    api_version = 1
#    entity_name = 'users'
#    http_method = 'GET'
#
#    # Send the analytics tracking data - ONLY FOR DEBUGGING
#    for i in range(1, 21):
#        print "NUM: {}".format(i)
#        print track_request(
#            piwik_host='app1.dev.apitrary.net',
#            piwik_site_id='3',
#            piwik_rec='1',
#            api_id=api_id,
#            api_version=api_version,
#            http_method=http_method,
#            entity_name=entity_name
#        )
