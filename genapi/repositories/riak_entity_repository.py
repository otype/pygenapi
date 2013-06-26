# -*- coding: utf-8 -*-
"""

    pygenapi

    by hgschmidt

    Copyright (c) 2012 apitrary

"""
import logging
import riak
from genapi.errors import RiakObjectNotFoundException
from genapi.errors import RiakObjectIdNotProvidedException


class RiakEntityRepository(object):
    """
        Processor to handle the GET request.
    """

    def __init__(self, riak_client, bucket, bucket_name):
        """
            Simple init method ...
        """
        super(RiakEntityRepository, self).__init__()

        # Set the Riak client, bucket name and bucket
        self.riak_client = riak_client
        self.bucket_name = bucket_name
        self.bucket = bucket

    def fetch(self, object_id):
        """
            Retrieve a single object with given object ID from Riak
        """
        if object_id is None:
            logging.error('No object ID provided! Object ID required.')
            raise RiakObjectIdNotProvidedException()

        single_object = self.bucket.get(object_id).get_data()
        if single_object is None:
            logging.error('Object with given id={} not found!'.format(object_id))
            raise RiakObjectNotFoundException()
        else:
            single_object = self.bucket.get(object_id).get_data()

        return single_object

    def fetch_all(self):
        """
            This is a helper function to run a map/reduce search call retrieving all objects within
            this entity's bucket.

            Used in GET (EntityHandlers).
        """
        # return [[v.key, data]];
        query = riak.RiakMapReduce(self.riak_client).add(self.bucket_name)
        query.map('''function(v) {
                        var data = JSON.parse(v.values[0].data);
                        if(v.key != '_init') {
                            return [{'_data': data, '_id': v.key}];
                        }
                        return [];
                    }''')
        return query.run()

    def add(self, object_id, data):
        """
            Create a object in database
        """
        return self.bucket.new(object_id, data).store()

    def update(self, object_id, data):
        """
            Update a given object in database
        """
        return self.add(object_id=object_id, data=data)

    def remove(self, object_id):
        """
            Remove an object from Riak
        """
        return self.bucket.get(object_id).delete()