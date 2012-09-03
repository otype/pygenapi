# -*- coding: utf-8 -*-
"""

    GenAPI

    Entity Handlers

    This file contains the handler class for dynamically creating
    API end-points for a given entity. The entity name itself is not relevant as
    the end-point is defined in the main file. We are only interested in the bucket name
    of the underlying Riak database. Using the bucket, we only respond to HTTP verbs (CRUD).

    Copyright (c) 2012 apitrary

"""
import json
import logging
import uuid
import riak
import time
import tornado.ioloop
import tornado.web
import tornado.httpserver
import tornado.httputil
from base_handlers import BaseHandler

class SimpleEntityHandler(BaseHandler):
    """
        This handler is responsible for handling all CRUD operations and, additionally,
        search & receive_all calls.

        It will respond to following HTTP verbs and URLs:

        GET     '/<entity_name>'
        GET     '/<entity_name>/([0-9a-zA-Z]+)'
        GET     '/<entity_name>?q=<key>:<search_value>'
        POST    '/<entity_name>'
        PUT     '/<entity_name>/([0-9a-zA-Z]+)'
        DELETE  '/<entity_name>/([0-9a-zA-Z]+)'
    """

    # Set of supported methods for this resource
    SUPPORTED_METHODS = ("GET", "POST", "PUT", "DELETE")

    def __init__(self, application, request, bucket_name, riak_rq, riak_wq, **kwargs):
        """
            Sets up the Riak client and the bucket
        """
        super(SimpleEntityHandler, self).__init__(application, request, **kwargs)

        self.bucket_name = bucket_name
        logging.debug('Entity bucket = "{}"'.format(self.bucket_name))

        # Setup the Riak bucket
        self.bucket = self.client.bucket(self.bucket_name).set_r(riak_rq).set_w(riak_wq)

    def fetch_all(self):
        """
            This is a helper function to run a map/reduce search call retrieving all objects within
            this entity's bucket.
        """
        query = riak.RiakMapReduce(self.client).add(self.bucket_name)
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

    def search(self, question):
        """
            Search within this entity's bucket.
        """
        query = self.client.search(self.bucket_name, question)
        logging.debug('search_query: {}'.format(query))
        response = []
        for result in query.run():
            # Getting ``RiakLink`` objects back.
            obj = result.get()
            obj_data = obj.get_data()
            kv_object = {'_id': result._key, '_data': obj_data}
            response.append(kv_object)

        return response

    def get_single_object(self, object_id):
        """
            Retrieve blog post with given id
        """
        return self.bucket.get(object_id).get_data()

    #noinspection PyMethodOverriding
    def get(self, object_id=None):
        """
            Fetch a set of objects. If user doesn't provide a query (e.g. place:Hann*), then
            we assume the user wants to have all objects in this bucket.
        """
        # TODO: Add another way to limit the query results (fetch_all()[:100])
        # TODO: Add another way to query for documents after/before a certain date

        if object_id:
            self.write(self.get_single_object(object_id))
            self.finish()
        else:
            query = self.get_argument('q', default=None)

            results = ''
            try:
                if query:
                    results = self.search(query)
                else:
                    results = self.fetch_all()
                self.write({'results': results})
            except Exception, e:
                logging.error(e)
                self.write_error(500, message='Error on fetching all objects!')

    def post(self, *args, **kwargs):
        """
            Stores a new blog post into Riak
        """
        object_id = uuid.uuid1().hex
        logging.debug("created new object id: {}".format(object_id))
        try:
            obj_to_store = json.loads(unicode(self.request.body, 'latin-1'))
            if obj_to_store is None:
                raise tornado.web.HTTPError(400)

            # add time stamps
            obj_to_store['_createdAt'] = time.time()
            obj_to_store['_updatedAt'] = time.time()

            # Check if this post is valid
            result = self.bucket.new(object_id, obj_to_store).store()
            self.set_status(201)
            self.write({"id": result._key})
        except ValueError:
            self.write_error(500, message='Cannot store object!')
        except Exception, e:
            self.write_error(500, message=e.value)

    def put(self, object_id=None):
        """
            Stores a new blog post into Riak
        """
        if object_id is None:
            raise tornado.web.HTTPError(400, log_message="Missing object id")

        # First, try to get the object (check if it exists)
        db_object = self.bucket.get(object_id).get_data()

        if db_object is None:
            self.write_error(410, message='Cannot update object: object with given id does not exist!')
            return

        try:
            obj_to_store = json.loads(unicode(self.request.body, 'latin-1'))
            if obj_to_store is None:
                raise tornado.web.HTTPError(
                    304,
                    log_message='Updating object with id: {} not possible.'.format(object_id)
                )

            # TODO: Currently, a PUT will overwrite the existing object ... therefore, we always have a new _createdAt. Fix this!
            # update time stamp
            obj_to_store['_createdAt'] = time.time()
            obj_to_store['_updatedAt'] = time.time()

            # Check if this post is valid
            updated_object = self.bucket.new(object_id, data=obj_to_store).store()
            self.write({"id": updated_object._key})
        except ValueError:
            self.write_error(500, message='Cannot store object!')
        except Exception, e:
            self.write_error(500, message=e.value)

    def delete(self, object_id=None):
        """
            Stores a new blog post into Riak
        """
        if object_id is None:
            raise tornado.web.HTTPError(400, log_message="Missing object id")

        object_to_store = self.bucket.get(object_id)
        if object_to_store.get_data() is None:
            raise tornado.web.HTTPError(410, log_message='Object with id: {} does not exist.'.format(object_id))

        result = object_to_store.delete()
        if result.get_data() is None:
            logging.debug("Deleted object with id: {}".format(object_id))
            self.set_status(200)
            self.write({"deleted": object_id})
        else:
            raise tornado.web.HTTPError(410, log_message='Could not delete object with id: {}'.format(object_id))

