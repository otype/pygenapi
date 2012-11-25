# -*- coding: utf-8 -*-
"""

    pygenapi

    by hgschmidt

    Copyright (c) 2012 apitrary

"""
import logging
from services.base_service import BaseService

class SearchService(BaseService):
    """
        All search-related service methods
    """

    def __init__(self, headers, riak_client, bucket, bucket_name):
        """
            Additionally, add the RiakService.
        """
        super(SearchService, self).__init__(headers)

        # Set the Riak client, bucket name and bucket
        self.riak_client = riak_client
        self.bucket_name = bucket_name
        self.bucket = bucket


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

        return search_response

