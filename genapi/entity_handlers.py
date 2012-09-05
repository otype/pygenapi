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
import time
import tornado.ioloop
import tornado.web
import tornado.httpserver
import tornado.httputil
from analytics import send_analytics_data
from base_handlers import BaseHandler
from entity_handlers_helpers import get_single_object, search, fetch_all, illegal_attributes_exist

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

    def __init__(self, application, request, bucket_name, riak_rq, riak_wq, api_id, api_version, entity_name, **kwargs):
        """
            Sets up the Riak client and the bucket
        """
        super(SimpleEntityHandler, self).__init__(application, request, **kwargs)

        # Tell us a bit about the request
        logging.debug(request)

        # track in GA
        send_analytics_data(
            remote_ip=request.remote_ip,
            user_agent=request.headers['User-Agent'],
            api_id=api_id,
            api_version=api_version,
            entity_name=entity_name
        )

        # The constructed bucket name
        self.bucket_name = bucket_name
        logging.debug('Entity bucket = "{}"'.format(self.bucket_name))

        # Setup the Riak bucket
        self.bucket = self.client.bucket(self.bucket_name).set_r(riak_rq).set_w(riak_wq)


    def get(self, object_id=None):
        """
            Fetch a set of objects. If user doesn't provide a query (e.g. place:Hann*), then
            we assume the user wants to have all objects in this bucket.
        """
        # TODO: Add another way to limit the query results (fetch_all()[:100])
        # TODO: Add another way to query for documents after/before a certain date

        if object_id:
            self.write(get_single_object(self.bucket, object_id))
            return

        # No object id? Ok, we'll continue with search/fetch_all
        query = self.get_argument('q', default=None)
        try:
            if query:
                results = search(self.client, self.bucket_name, query)
            else:
                results = fetch_all(self.client, self.bucket_name)

            self.write({'results': results})
        except Exception, e:
            logging.error("Maybe too quick here? Error: {}".format(e))
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

            if illegal_attributes_exist(obj_to_store):
                self.write_error(
                    400,
                    message='Object contains keys starting with illegal characters, e.g. an underscore.'
                )
                return

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
            self.write_error(500, message=e)


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

            if illegal_attributes_exist(obj_to_store):
                self.write_error(
                    400,
                    message='Object contains keys starting with illegal characters, e.g. an underscore.'
                )
                return

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
            self.write_error(500, message=e)


    def delete(self, object_id=None):
        """
            Stores a new blog post into Riak
        """
        if object_id is None:
            raise tornado.web.HTTPError(400, log_message="Missing object id")

        db_obj = self.bucket.get(object_id)
        if db_obj.get_data() is None:
            raise tornado.web.HTTPError(410, log_message='Object with id: {} does not exist.'.format(object_id))

        result = db_obj.delete()
        if result.get_data() is None:
            logging.debug("Deleted object with id: {}".format(object_id))
            self.set_status(200)
            self.write({"deleted": object_id})
        else:
            raise tornado.web.HTTPError(410, log_message='Could not delete object with id: {}'.format(object_id))
