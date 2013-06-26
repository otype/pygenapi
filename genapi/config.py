# -*- coding: utf-8 -*-
"""

    GenAPI

    Copyright (c) 2012 apitrary

"""

APP_DETAILS = {
    'name': 'PyGenAPI',
    'version': '0.5.3.8',
    'company': 'apitrary',
    'support': 'http://apitrary.com/support',
    'contact': 'support@apitrary.com',
    'copyright': '2012 apitrary.com',
}

COOKIE_SECRET = 'Pa1eevenie-di4koGheiKe7ki_inoo2quiu0Xohhaquei4thuv98hs9dfb9*B(FBS(FB9sdbvs9dbv'
TORNADO_APP_SETTINGS = {
    'cookie_secret': COOKIE_SECRET,
    'xheaders': True
}

GOOGLE_ANALYTICS = {
    'STAGING': "MO-28942332-9",         # STAGING ENVIRONMENT GA
    'LIVE': "MO-28942332-3"             # LIVE ENVIRONMENT GA
}

ZMQ = {
    'TRACKR_CONNECT_ADDRESS': "tcp://localhost:5555",  # ZMQ_SERVER is running locally (for now).
    'TRACKR_BIND_ADDRESS': "tcp://*:5555"   # ZMQ_SERVER is running locally (for now).
}

ILLEGAL_ATTRIBUTES_SET = ['_createdAt', '_updatedAt', '_init']
ILLEGAL_CHARACTER_SET = ['_', '__']
