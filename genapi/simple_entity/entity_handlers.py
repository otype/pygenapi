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
import tornado
from tornado import escape
from services.entity_service import EntityService
from services.search_service import SearchService
from simple_entity.base_handlers import BaseHandler
from simple_entity.entity_handlers_helpers import validate_user_agent
from simple_entity.entity_handlers_helpers import get_current_time_formatted
from simple_entity.entity_handlers_helpers import illegal_attributes_exist
from simple_entity.entity_handlers_helpers import filter_out_timestamps
from models.google_tracking_data import GoogleTrackingData
from tracking.tracking_worker import send_tracking_data_asynchronously


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
    SUPPORTED_METHODS = ("GET", "POST", "PUT", "DELETE", "OPTIONS")

    def __init__(self, application, request, bucket_name, riak_rq, riak_wq, api_id, api_version, env, entity_name,
                 api_key, **kwargs):
        """
            Sets up the Riak client and the bucket
        """
        super(SimpleEntityHandler, self).__init__(application, request, **kwargs)

        # The API Key
        self.api_key = api_key

        # Creating a GoogleTrackingData object with all necessary information we need from this
        # incoming request. The, send this tracking data as JSON to our ZMQ worker which will take
        # care of sending the data to Google ...
        send_tracking_data_asynchronously(
            str(
                GoogleTrackingData(
                    request=request,
                    user_agent=validate_user_agent(request=request),
                    api_id=api_id,
                    api_version=api_version,
                    env=env,
                    entity_name=entity_name
                ).as_json()
            )
        )

        # The constructed bucket name + setup the bucket
        logging.debug('Entity bucket = "{}"'.format(bucket_name))
        bucket = self.client.bucket(bucket_name).set_r(riak_rq).set_w(riak_wq)

        # Create required services
        self.entity_service = EntityService(
            headers=request.headers, riak_client=self.client, bucket_name=bucket_name, bucket=bucket
        )
        self.search_service = SearchService(
            headers=request.headers, riak_client=self.client, bucket_name=bucket_name, bucket=bucket
        )

    def get(self, object_id=None):
        """
            Fetch a set of objects. If user doesn't provide a query (e.g. place:Hann*), then
            we assume the user wants to have all objects in this bucket.
        """
        # Check the headers
        if self.require_headers() == 1:
            return

        try:
            # Object ID available? Then fetch the object!
            if object_id:
                self.respond(payload=self.entity_service.get(object_id=object_id))
                return

            # No object id? Ok, we'll continue with search/fetch_all
            query = self.get_argument('q', default=None)
            if query:
                self.respond(payload=self.search_service.search(query))
                return

            # No object id & no 'q'? Then, it's a regular GET ALL!
            self.respond(payload=self.entity_service.get_all())
        except ValueError, e:
            logging.error('Cannot convert JSON object. Error: {}'.format(e))
            self.write_error(500, message='Cannot convert JSON object!')
        except Exception, e:
            logging.error('General error: {}'.format(e))
            self.write_error(500, message='A general error occurred. Contact admin.')

    def post(self, *args, **kwargs):
        """
            Stores a new blog post into Riak
        """
        # Check the headers
        if self.require_headers(require_content_type=True) == 1:
            return

        # Generate a unique ID for the Riak object
        object_id = uuid.uuid1().hex
        logging.debug("created new object id: {}".format(object_id))
        try:
            # Load the JSON to see it's valid.
            obj_to_store = json.loads(tornado.escape.utf8(self.request.body), 'utf-8')

            # Check for illegal attributes (reserved words)
            if illegal_attributes_exist(obj_to_store):
                self.write_error(
                    status_code=400,
                    message='Object contains keys starting with reserved characters [\'_\', \'__\'].'
                )
                return

            # add time stamps
            obj_to_store['_createdAt'] = obj_to_store['_updatedAt'] = get_current_time_formatted()

            # Check if this post is valid
            result = self.entity_service.post(object_id=object_id, data=obj_to_store)
            self.respond(status_code=201, payload={"_id": result._key, "_data": result.get_data()})
        except ValueError, e:
            logging.error('Cannot convert JSON object. Error: {}'.format(e))
            self.write_error(500, message='Cannot convert JSON object!')
        except Exception, e:
            logging.error('General error: {}'.format(e))
            self.write_error(500, message='A general error occurred. Contact admin.')

    def put(self, object_id=None):
        """
            Stores a new blog post into Riak
        """
        # Check the headers
        if self.require_headers(require_content_type=True) == 1:
            return

        # Object Id provided?
        if object_id is None:
            self.set_status(400)
            self.write_error(400, message="Missing object ID!")

        # First, try to get the object (check if it exists)
        db_object = self.entity_service.get(object_id)
        if db_object is None:
            self.write_error(404, message='Cannot update object: object with given id does not exist!')
            return

        try:
            obj_to_store = json.loads(unicode(self.request.body, 'latin-1'))
            if obj_to_store is None:
                self.write_error(400, message='Updating object with id: {} not possible.'.format(object_id))
                return

            # Filter out the time stamps if they exist
            obj, created_at, updated_at = filter_out_timestamps(obj_to_store)

            # Check if keys exist with illegally starting characters
            if illegal_attributes_exist(obj_to_store):
                self.write_error(
                    400,
                    message='Object contains keys starting with illegal characters, e.g. an underscore.'
                )
                return

            # update time stamp
            obj_to_store['_createdAt'] = obj_to_store['_updatedAt'] = get_current_time_formatted()
            if created_at:
                obj_to_store['_createdAt'] = created_at

            # Check if this post is valid
            updated_object = self.entity_service.update(object_id=object_id, data=obj_to_store)
            self.respond(status_message='No data content', payload={"_id": updated_object._key, "_data": ""})
        except ValueError, e:
            logging.error('Cannot convert JSON object. Error: {}'.format(e))
            self.write_error(500, message='Cannot convert JSON object!')
        except Exception, e:
            logging.error('General error: {}'.format(e))
            self.write_error(500, message='A general error occurred. Contact admin.')

    def delete(self, object_id=None):
        """
            Stores a new blog post into Riak
        """
        # Check the headers
        if self.require_headers() == 1:
            return

        # Object ID was provided?
        if object_id is None:
            self.write_error(400, message="Missing object ID!")
            return

        # Check if we actually have an object with that ID
        if self.entity_service.get(object_id) is None:
            logging.error('Object with id: {} does not exist.'.format(object_id))
            self.write_error(404, message='Object with id: {} does not exist.'.format(object_id))
            return

        # Ok, delete the object with given object id
        if self.entity_service.delete(object_id).get_data() is None:
            logging.debug("Deleted object with id: {}".format(object_id))
            self.respond(status_message='Deleted', payload={"_id": object_id, "_data": ""})
            return

        # All failed?
        self.write_error(404, message='Could not delete object with id: {}'.format(object_id))

    def options(self, *args, **kwargs):
        """
            Returning back the list of suported HTTP methods
        """
        self.set_status(200)
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Methods", ', '.join([str(x) for x in self.SUPPORTED_METHODS]))
        self.write("ok")

    def require_headers(self, require_api_key=True, require_content_type=False, require_accept=True):
        """
            Helper for checking the required header variables
        """
        # Authorize request by enforcing API key (X-API-Key)
        if require_api_key:
            if self.entity_service.get_key_from_header('X-Api-Key') != self.api_key:
                self.write_error(status_code=401, message='Invalid API Key.')
                return 1

        # Enforce application/json as Accept
        if require_accept:
            if not self.entity_service.has_valid_accept_type():
                self.write_error(status_code=406, message='Accept is not application/json.')
                return 1

        # Enforce application/json as content-type
        if require_content_type:
            if not self.entity_service.has_valid_content_type():
                self.write_error(status_code=406, message='Content-Type is not set to application/json.')
                return 1

        # All good
        return 0