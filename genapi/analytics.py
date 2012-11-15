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
import uuid
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
    return '{api_id}{remote_ip}{user_agent}{uuid}'.format(
        api_id=api_id,
        remote_ip=remote_ip,
        user_agent=user_agent,
        uuid=uuid.uuid4()
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

        Please note the GA limits:

        Maximum number of accounts: 100+
        Maximum number of profiles per account: 50
        Maximum number of requests per single session visit: 500
        Maximum requests per 5 seconds: 10
        Number of characters in report filter: 256
        Number of statements in an advanced segment: None
        Number of rows per report: 500-unlimited
        Maximum number of visits per day: 50,000
        Maximum number of page views: 10 million

        Overall API Limits
        - 50,000 requests per project per day
        - 10 queries per second (QPS) per IP
        - No more than 4 requests at the same time. (per IP address)
        - No more than 10 requests for ALL Google API per IP address within a given 1 second period.

        Core Reporting API Limits
        - 10,000 requests per profile per day
        - 10 concurrent requests per profile

        Check:
        http://www.quora.com/Google-Analytics/What-are-the-absolute-limits-of-Google-Analytics-accounts

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
