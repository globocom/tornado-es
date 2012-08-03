# -*- coding: utf-8 -*-

import json

from tornado.httpclient import AsyncHTTPClient, HTTPRequest
from tornado.ioloop import IOLoop
from urllib import urlencode


class ESConnection(object):

    def __init__(self, host='localhost', port= '9200', io_loop=None):
        self.io_loop = io_loop or IOLoop.instance()
        self.host = host
        self.port = port
        self.client = AsyncHTTPClient(self.io_loop)

    def create_path(self, method,**kwargs):
        index = kwargs.get('index', '_all')
        type_ = '/' + kwargs.get('type') if kwargs.has_key('type') else ''
        size = kwargs.get('size', 10)
        page = kwargs.get('page', 1)
        from_ = (page-1)*size
        jsonp_callback = kwargs.get('jsonp_callback', '')
        path = "/%(index)s%(type)s/_%(method)s?%(querystring)s%(jsonp_callback)s" % {
                    "querystring":urlencode({'from': from_, 'size': size}),
                    "method": method,
                    "index":index,
                    "type": type_,
                    "jsonp_callback": "&callback=" + jsonp_callback if jsonp_callback else ""
                    }
        return path

    def search(self, callback, **kwargs):
        path = self.create_path("search", **kwargs)
        source = json.dumps( kwargs.get('source', {"query":{"query_string" : {"query" : "*"}}}))
        self.post_by_path(path, callback, source)

    def multi_search(self, callback, **kwargs):
        path = self.create_path("msearch", **kwargs)
        source = kwargs.get('source', {"query":{"query_string" : {"query" : "*"}}})
        self.post_by_path(path, callback, source)

    def post_by_path(self, path, callback, source):
        url = 'http://%(host)s:%(porta)s%(path)s' % {"host": self.host, "porta": self.port, "path": path}
        request_http = HTTPRequest(url, method="POST", body=source)
        self.client.fetch(request_http, callback)

    def get_by_path(self, path, callback):
        url = 'http://%(host)s:%(porta)s%(path)s' % {"host": self.host, "porta": self.port, "path": path}
        self.client.fetch(url, callback)
