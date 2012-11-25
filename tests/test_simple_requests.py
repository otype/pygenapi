# -*- coding: utf-8 -*-
"""

    pygenapi

    by hgschmidt

    Copyright (c) 2012 apitrary

"""
import json
from time import sleep
import tornado
from tornado import httpclient
from tornado.httpclient import HTTPError

class TestSimpleEntity(object):
    def __init__(self):
        super(TestSimpleEntity, self).__init__()
        self.async_client = tornado.httpclient.AsyncHTTPClient()
        self.client = tornado.httpclient.HTTPClient()
        self.db_key = ''
        self.test_url = 'http://localhost:7000/user'

#    def setUp(self):
#        self.db_key = 'e56b491136fc11e2b7f4e0f84717e184'

    def test_simple_entity_get_all(self):
        response = self.client.fetch(self.test_url, method='GET')
        assert response.code == 200
        content_type = response.headers['Content-Type']
        assert content_type == 'application/json; charset=UTF-8'

    def test_simple_entity_get_and_post_and_put_and_delete(self):
        # Testing POST
        response = self.client.fetch(
            self.test_url,
            method='POST',
            body=json.dumps({'a_key': 'a_value'}),
            headers={'Accept': 'application/json'}
        )
        sleep(1.0) # give time to settle
        resp = json.loads(response.body)
        self.db_key = resp['result']['_id']
        assert self.db_key != ''
        assert response.code == 201
        assert resp['statusCode'] == 201
        content_type = response.headers['Content-Type']
        assert content_type == 'application/json; charset=UTF-8'

        # Testing GET in the same test (due to Key)
        response = self.client.fetch(
            '{}/{}'.format(self.test_url, self.db_key),
            method='GET',
            headers={'Content-Type': 'application/json', 'Accept': 'application/json'}
        )
        sleep(1.0) # give time to settle
        resp = json.loads(response.body)
        assert response.code == 200
        assert resp['statusCode'] == 200
        content_type = response.headers['Content-Type']
        assert content_type == 'application/json; charset=UTF-8'

        # Testing PUT
        response = self.client.fetch(
            '{}/{}'.format(self.test_url, self.db_key),
            method='PUT',
            body=json.dumps({'a_key': 'a_value', 'another_key': 'another_value'}),
            headers={'Content-Type': 'application/json', 'Accept': 'application/json'}
        )
        sleep(1.0) # give time to settle
        resp = json.loads(response.body)
        assert resp['result']['_data'] == ''
        assert response.code == 200
        assert resp['statusCode'] == 200
        content_type = response.headers['Content-Type']
        assert content_type == 'application/json; charset=UTF-8'

        # Testing DELETE
        response = self.client.fetch(
            '{}/{}'.format(self.test_url, self.db_key),
            method='DELETE',
            headers={'Accept': 'application/json'}
        )
        sleep(1.5) # give time to settle
        resp = json.loads(response.body)
        assert resp['statusMessage'] == 'Deleted'
        assert response.code == 200
        assert resp['statusCode'] == 200
        content_type = response.headers['Content-Type']
        assert content_type == 'application/json; charset=UTF-8'

        # Now, delete again ... this should fail
        try:
            response = self.client.fetch(
                '{}/{}'.format(self.test_url, self.db_key),
                method='DELETE'
            )
        except HTTPError, e:
            pass
