# -*- coding: utf-8 -*-
"""

    GenAPI

    Copyright (c) 2012 apitrary

"""
import json
import logging
import riak
from config import ILLEGAL_CHARACTER_SET

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
        for key in obj.viewkeys():
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
    query.map('function(v) { var data = JSON.parse(v.values[0].data); return [[v.key, data]]; }')
    query.reduce('''function(v) {
                var result = [];
                for(val in v) {
                    temp_res = {};
                    temp_res['_id'] = v[val][0];
                    temp_res['_data'] = v[val][1];
                    result.push(temp_res);
                }
                return result;
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
