#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
"""

    GenAPI

    Start GenAPI:

    $ python ./start.py --port=7000 --riak_host=localhost --api_version=1 \
      --api_id=aaaaaaaa --entity=user,object,contact


    Copyright (c) 2012 apitrary

"""
from tornadoriak.runner import run_server
from tornadoriak.base_entity_handler import BaseEntityHandler
from tornadoriak.handler_helpers import validate_user_agent
from genapi.tracking import TrackingService
from genapi.tracking import GoogleTrackingData


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

    def __init__(self, application, request, bucket_name, riak_rq, riak_wq, api_id, api_version, env, entity_name,
                 api_key, **kwargs):
        """
                    Sets up the Riak client and the bucket
                """
        super(SimpleEntityHandler, self).__init__(application, request, bucket_name, riak_rq, riak_wq, **kwargs)
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


def main():
    """
        Start the server
    """
    COOKIE_SECRET = 'oe1aux0oa5ooCh&oo.qu6lie4wei2XiuXieM1eifooth3ai>goosugh3ees;ah"kiephahc7aghaerooGh2Xaa%zie:haepho'
    run_server(entity_handler=SimpleEntityHandler, cookie_secret=COOKIE_SECRET)

# MAIN
#
#
if __name__ == "__main__":
    main()
