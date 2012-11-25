# -*- coding: utf-8 -*-
"""

    GenAPI

    Copyright (c) 2012 apitrary

"""

def get_bucket_name(api_id, entity_name):
    """
        To create uniform bucket names
    """
    return '{}_{}'.format(api_id, entity_name)
