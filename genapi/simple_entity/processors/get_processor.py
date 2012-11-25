# -*- coding: utf-8 -*-
"""

    pygenapi

    by hgschmidt

    Copyright (c) 2012 apitrary

"""
import logging
import riak
from response import Response
from simple_entity.processors.base_processor import BaseProcessor

class GetService(BaseProcessor):
    """
        Processor to handle the GET request.
    """

    def fetch(self, object_id):
        """
            Retrieve a single object with given object ID from Riak
        """
        if object_id is None:
            logging.error('No object ID provided! Object ID required.')
            return Response(status_code=404, status_message='No object ID provided! Object ID required.', result={})

        # Fetch the data from the Riak bucket
        single_object = self.bucket.get(object_id).get_data()

        # No object retrieved? Key must be invalid.
        if single_object is None:
            logging.error('Object with given id={} not found!'.format(object_id))
            return Response(status_code=404, status_message='Object with given id not found!', result={})

        return Response(status_code=200, status_message='OK', result={"_id": object_id, "_data": single_object})

    def fetch_all(self):
        """
            This is a helper function to run a map/reduce search call retrieving all objects within
            this entity's bucket.

            Used in GET (EntityHandlers).
        """
        # TODO: Add another way to limit the query results (fetch_all()[:100])
        query = riak.RiakMapReduce(self.riak_client).add(self.bucket_name)
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
        fetch_results = query.run()
        return Response(status_code=200, status_message='OK', result=fetch_results)

    def search(self, search_query):
        """
            Search within this entity's bucket.

            Used in GET (EntityHandlers).
        """
        # TODO: Add another way to query for documents after/before a certain date
        search_query = self.riak_client.search(self.bucket_name, search_query)
        logging.debug('search_query: {}'.format(search_query))
        search_response = []
        for result in search_query.run():
            # Getting ``RiakLink`` objects back.
            obj = result.get()
            obj_data = obj.get_data()
            kv_object = {'_id': result._key, '_data': obj_data}
            search_response.append(kv_object)

        return Response(status_code=200, status_message='OK', result=search_response)
