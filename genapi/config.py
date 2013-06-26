# -*- coding: utf-8 -*-
"""

    GenAPI

    Copyright (c) 2012 apitrary

"""

APP_DETAILS = {
    'name': 'PyGenAPI',
    'version': '0.5.3.10',
    'company': 'apitrary',
    'support': 'http://apitrary.com/support',
    'contact': 'support@apitrary.com',
    'copyright': '(c) 2012 - 2013 apitrary.com',
}

COOKIE_SECRET = 'Pa1eevenie-di4koGheiKe7ki_inoo2quiu0Xohhaquei4thuv98hs9dfb9*B(FBS(FB9sdbvs9dbv'
TORNADO_APP_SETTINGS = {
    'cookie_secret': COOKIE_SECRET,
    'xheaders': True
}

ILLEGAL_ATTRIBUTES_SET = ['_createdAt', '_updatedAt', '_init']
ILLEGAL_CHARACTER_SET = ['_', '__']
