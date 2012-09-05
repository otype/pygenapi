# -*- coding: utf-8 -*-
"""

    GenAPI

    Copyright (c) 2012 apitrary

"""
import logging
import riak

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