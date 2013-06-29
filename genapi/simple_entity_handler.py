# -*- coding: utf-8 -*-
"""

    pygenapi

    by hgschmidt

    Copyright (c) 2012 apitrary

"""
from tornadoriak.base_entity_handler import BaseEntityHandler
from tornadoriak.handler_helpers import validate_user_agent
from genapi.tracking import TrackingService, GoogleTrackingData


class SimpleEntityHandler(BaseEntityHandler):
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

    def __init__(self, application, request, bucket_name, riak_rq, riak_wq, api_id, api_version, env,
                 entity_name, **kwargs):
        """
            Sets up the Riak client and the bucket
        """
        super(SimpleEntityHandler, self).__init__(application, request, bucket_name, riak_rq, riak_wq, **kwargs)
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

        return 0