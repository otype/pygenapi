# -*- coding: utf-8 -*-
"""

    GenAPI

    Copyright (c) 2012 apitrary

"""

# Application details
APP_DETAILS = {
    'name': 'PyGenAPI',
    'version': '0.5.2',
    'company': 'apitrary',
    'support': 'http://apitrary.com/support',
    'contact': 'support@apitrary.com',
    'copyright': '2012 apitrary.com',
}

# Cookie secret
COOKIE_SECRET = 'Pa1eevenie-di4koGheiKe7ki_inoo2quiu0Xohhaquei4thuv'

# General app settings for Tornado
APP_SETTINGS = {
    'cookie_secret': COOKIE_SECRET,
    'xheaders': True
}

GOOGLE_ANALYTICS = {
    'STAGING': "MO-28942332-9",         # STAGING ENVIRONMENT GA
    'LIVE': "MO-28942332-3"             # LIVE ENVIRONMENT GA
}

PIWIK = {
    'STAGING' : {
        'HOST': 'app1.dev.apitrary.net',
        'SITE_ID': '3',
        'REC': '1'
    }
}

ZMQ = {
    'TRACKR_CONNECT_ADDRESS': "tcp://localhost:5555",  # ZMQ_SERVER is running locally (for now).
    'TRACKR_BIND_ADDRESS': "tcp://*:5555"   # ZMQ_SERVER is running locally (for now).
}

ILLEGAL_ATTRIBUTES_SET = ['_createdAt', '_updatedAt', '_init']
ILLEGAL_CHARACTER_SET = ['_', '__']
