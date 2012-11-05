# -*- coding: utf-8 -*-
"""

    GenAPI

    Copyright (c) 2012 apitrary

"""

# Application details
APP_DETAILS = {
    'name': 'PyGenAPI',
    'version': '0.3.3',
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
    'dev_account_id': "UA-28942332-7",         # TEST ENVIRONMENT GA
    'live_account_id': "UA-28942332-3"         # LIVE ENVIRONMENT GA
}

ILLEGAL_ATTRIBUTES_SET = ['_createdAt', '_updatedAt', '_init']
ILLEGAL_CHARACTER_SET = ['_']
