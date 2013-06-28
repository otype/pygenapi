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
from tornadoriak.entity_handler import EntityHandler
from tornadoriak.handler_helpers import validate_user_agent
from genapi.tracking import TrackingService
from genapi.tracking import GoogleTrackingData


class SimpleEntityHandler(EntityHandler):
    """
        This handler is responsible for handling all CRUD operations and, additionally,
        search & receive_all calls.

        It will respond to following HTTP verbs and URLs:

        GET     '/<entity_name>'
        GET     '/<entity_name>.json'
        GET     '/<entity_name>/([0-9a-zA-Z]+)'
        GET     '/<entity_name>/([0-9a-zA-Z]+).json'
        GET     '/<entity_name>?q=<key>:<search_value>'
        POST    '/<entity_name>'
        PUT     '/<entity_name>/([0-9a-zA-Z]+)'
        DELETE  '/<entity_name>/([0-9a-zA-Z]+)'
    """

    def __init__(self, application, request, bucket_name, riak_rq, riak_wq, api_id, api_version, env, entity_name,
                 api_key, **kwargs):
        """
                Sets up the Riak client and the bucket
            """
        super(SimpleEntityHandler, self).__init__(application, request, bucket_name, riak_rq, riak_wq, api_key, **kwargs)
        self.api_key = api_key
        tracking_service = TrackingService()
        tracking_service.send_data_to_trackr(
            GoogleTrackingData(
                request=request,
                user_agent=validate_user_agent(request=request),
                api_id=api_id,
                api_version=api_version,
                env=env,
                entity_name=entity_name
            )
        )
