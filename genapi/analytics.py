# -*- coding: utf-8 -*-
"""

    GenAPI - Analytics library

    Copyright (c) 2012 apitrary

"""
import logging
from random import randint
from urllib import urlencode
from urllib2 import urlopen
from urlparse import urlunparse
from hashlib import sha1
from genapi.config import GOOGLE_ANALYTICS


def send_data_to_google_analytics(ga_account_id, ga_visitor_id, called_path):
    """
        Google Analytics magic.

        Also check:
        http://www.tutkiun.com/2011/04/a-google-analytics-cookie-explained.html
    """
    # Generate the visitor identifier somehow. I get it from the
    # environment, calculate the SHA1 sum of it, convert this from base 16
    # to base 10 and get first 10 digits of this number.
    visitor = str(int("0x%s" % sha1(ga_visitor_id).hexdigest(), 0))[:10]
    logging.debug("Generated visitor ID: {}".format(visitor))

    # Collect everything in a dictionary
    DATA = {"utmwv": "5.2.2d",                      # Tracking code version
            "utmn": str(randint(1, 9999999999)),    # Unique ID generated to each GIF request preventing caching
            "utmp": called_path,                    # The called path
            "utmac": ga_account_id,                 # GA profile identifier
            "utmcc": "__utma=%s;" % ".".join([
                "1",        # Domain hash, unique for each domain
                visitor,    # Unique Identifier (Unique ID)
                "1",        # Timestamp of time you first visited the site
                "1",        # Timestamp for the previous visit
                "1",        # Timestamp for the current visit
                "1"         # Number of sessions started
            ])}

    # Encode this data and generate the final URL
    URL = urlunparse(("http",
                      "www.google-analytics.com",
                      "/__utm.gif",
                      "",
                      urlencode(DATA),
                      ""))
    # Make the request
    logging.debug("Requesting URL: {}".format(URL))
    ga_response = urlopen(URL)
    logging.debug("Sent data: \n{}".format(ga_response.info()))


def generate_unique_user_id(api_id, remote_ip, user_agent):
    """
        Generates a unique user id which will be sent to GA.
        We need this to distinguish between different users/clients.
    """
    # TODO: Request UUID/AndroidUniqueID from SDK or all clients (possible: via Header variable)
    # For mobile, it should be following:
    # '{api_id}{uuid}{user_agent}'
    return '{api_id}{remote_ip}{user_agent}'.format(
        api_id=api_id,
        remote_ip=remote_ip,
        user_agent=user_agent
    )

def get_ga_profile(env):
    """
        Load the corresponding profile code for the environment
    """
    if env.lower() == 'dev':
        return GOOGLE_ANALYTICS['STAGING']
    if env.lower() == 'staging':
        return GOOGLE_ANALYTICS['STAGING']
    elif env.lower() == 'live':
        return GOOGLE_ANALYTICS['LIVE']
    else:
        return GOOGLE_ANALYTICS['STAGING']

##############################################################################
#
# Trigger analytics call
#
##############################################################################


def send_analytics_data(remote_ip, user_agent, api_id, api_version, env, entity_name):
    """
        Trigger the Analytics call by sending the request information to
        Google Analytics.
    """
    # We are creating here the GA visitor id, based on various information
    ga_visitor_id = generate_unique_user_id(api_id, remote_ip, user_agent)

    # Track this request in GA
    ga_path = '{api_id}/v{api_version}/{entity_name}'.format(
        api_id=api_id,
        api_version=api_version,
        entity_name=entity_name
    )

    # Finally, send the request to Google Analytics
    send_data_to_google_analytics(
        ga_account_id=get_ga_profile(env),
        ga_visitor_id=ga_visitor_id,
        called_path=ga_path
    )
