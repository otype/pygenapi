# -*- coding: utf-8 -*-
"""

    pygenapi

    by hgschmidt

    Copyright (c) 2012 - 2013 apitrary

"""
from services.trackr_service import TrackrService

class TrackingService(object):
    """
        Provide calls for sending tracking data to Google Analytics, Piwik, etc.
    """

    def send_data_to_trackr(self, tracking_data):
        """
            Send tracking data to Trackr method
        """
        trackr_service = TrackrService()
        trackr_service.send_tracking_data_asynchronously(tracking_data=str(tracking_data.as_json()))
