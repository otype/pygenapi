# -*- coding: utf-8 -*-
"""

    GenAPI

    Copyright (c) 2012 apitrary

"""
import json
import logging
import riak
from settings.config import ILLEGAL_CHARACTER_SET


def pop_field(obj, field):
    """
        Pop a given field from given dictionary object.
    """
    popped_field = None
    if obj is None:
        return obj, popped_field

    if field is None:
        return obj, popped_field

    if field in obj:
        popped_field = obj.pop(field)

    return obj, popped_field


def filter_out_timestamps(obj):
    """
        If a PUT request body has the original _createdAt and _updatedAt fields, we don't want
        to prohibit the request (see illegal_attributes_exist()). Instead, the user should be
        able to simply send the whole JSON again with updated attributes. What we can do here is
        to filter out those two keys and let the rest pass on. But: On PUT we should remember the
        _createdAt value and put it back in again.
    """
    created_at = None
    updated_at = None

    if '_createdAt' in obj:
        created_at = obj.pop('_createdAt')
    if '_updatedAt' in obj:
        updated_at = obj.pop('_updatedAt')

    return obj, created_at, updated_at


def illegal_attributes_exist(obj):
    """
        Check a given JSON object (or something that looks like a JSON string)
        for illegal keys, e.g. starting with '_'. If such illegal keys have been
        found, we report back immediately so that this object should be blocked.
    """
    if type(obj) == str:
        obj = json.loads(obj)
    elif type(obj) == unicode:
        obj = json.loads(obj)

    if type(obj) == dict:
        for key in obj.keys():
            for illegal_character in ILLEGAL_CHARACTER_SET:
                if key.startswith(illegal_character):
                    return True
    return False


def fetch_all(client, bucket_name):
    """
        This is a helper function to run a map/reduce search call retrieving all objects within
        this entity's bucket.

        Used in GET (EntityHandlers).
    """
    query = riak.RiakMapReduce(client).add(bucket_name)
    query.map('''function(v) {
                        var data = JSON.parse(v.values[0].data);
                        if(v.key != '_init') {
                            return [[v.key, data]];
                        }
                        return [];
                    }''')
    return query.run()


def search(client, bucket_name, query):
    """
        Search within this entity's bucket.

        Used in GET (EntityHandlers).
    """
    query = client.search(bucket_name, query)
    logging.debug('search_query: {}'.format(query))
    response = []
    for result in query.run():
        # Getting ``RiakLink`` objects back.
        obj = result.get()
        obj_data = obj.get_data()
        kv_object = {'_id': result._key, '_data': obj_data}
        response.append(kv_object)

    return response


def get_single_object(bucket, object_id):
    """
        Retrieve blog post with given id
    """
    return bucket.get(object_id).get_data()


def validate_user_agent(request):
    """
        Checks if a request has a User-agent set. If not
        we need to set a default string.
    """
    if 'User-Agent' not in request.headers:
        return 'UNKNOWN'
    else:
        return request.headers['User-Agent']


def is_content_type_application_json(headers):
    """
        Check if given request has content-type 'application/json'
    """
    content_type = get_key_from_header(headers, 'Content-Type')
    if content_type == 'application/json':
        return True
    else:
        return False


def get_key_from_header(headers, key_name):
    """
        Read a given key from header of given request
    """
    for k, v in headers.get_all():
        if k == key_name:
            return v
    return None
