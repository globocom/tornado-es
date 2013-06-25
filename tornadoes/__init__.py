# -*- coding: utf-8 -*-

import json

from models import BulkList

from urllib import urlencode
from tornado.ioloop import IOLoop
from tornado.httpclient import AsyncHTTPClient, HTTPRequest


class ESConnection(object):

    def __init__(self, host='localhost', port='9200', io_loop=None):
        self.io_loop = io_loop or IOLoop.instance()
        self.url = "http://%(host)s:%(port)s" % {"host": host, "port": port}
        self.bulk = BulkList()
        self.client = AsyncHTTPClient(self.io_loop)

    def create_path(self, method, **kwargs):
        index = kwargs.get('index', '_all')
        type_ = '/' + kwargs.get('type') if 'type' in kwargs else ''
        size = kwargs.get('size', 10)
        page = kwargs.get('page', 1)
        from_ = (page - 1) * size
        routing = kwargs.get('routing', '')
        jsonp_callback = kwargs.get('jsonp_callback', '')
        parameters = {'from': from_, 'size': size}
        if routing:
            parameters["routing"] = routing
        path = "/%(index)s%(type)s/_%(method)s?%(querystring)s%(jsonp_callback)s" % {
            "querystring": urlencode(parameters),
            "method": method,
            "index": index,
            "type": type_,
            "jsonp_callback": "&callback=" + jsonp_callback if jsonp_callback else ""
        }
        return path

    def search(self, callback, **kwargs):
        path = self.create_path("search", **kwargs)
        source = json.dumps(kwargs.get('source', {"query": {"query_string": {"query": "*"}}}))
        self.post_by_path(path, callback, source)

    def multi_search(self, index, source):
        self.bulk.add(index, source)

    def apply_search(self, callback):
        path = "/_msearch"
        source = self.bulk.prepare_search()
        self.post_by_path(path, callback, source=source)

    def post_by_path(self, path, callback, source):
        url = '%(url)s%(path)s' % {"url": self.url, "path": path}
        request_http = HTTPRequest(url, method="POST", body=source)
        self.client.fetch(request=request_http, callback=callback)

    def get_by_path(self, path, callback):
        url = '%(url)s%(path)s' % {"url": self.url, "path": path}
        self.client.fetch(url, callback)

    def get(self, index, type, uid, callback):
        def to_dict_callback(response):
            source = json.loads(response.body).get('_source', {})
            callback(source)
        path = '/{index}/{type}/{uid}'.format(**locals())
        url = '%(url)s%(path)s' % {"url": self.url, "path": path}
        self.client.fetch(url, to_dict_callback)
