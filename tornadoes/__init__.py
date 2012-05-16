# -*- coding: utf-8 -*-

import json

from tornado.httpclient import AsyncHTTPClient
from tornado.ioloop import IOLoop
from urllib import urlencode

class ESConnection(object):
    
    def __init__(self, host='localhost', port= '9200', io_loop=None):
        self.io_loop = io_loop or IOLoop.instance()
        self.host = host
        self.port = port
        self.client = AsyncHTTPClient(self.io_loop)

    def search(self, callback, **kwargs):
        index = kwargs.get('index', '_all')
        type_ = '/' + kwargs.get('type') if kwargs.has_key('type') else ''
        size = kwargs.get('size', 10)
        page = kwargs.get('page', 1)
        from_ = (page-1)*size
        source = json.dumps( kwargs.get('source', {"query":{"query_string" : {"query" : "*"}}}))
        path = "/%(index)s%(type)s/_search?%(querystring)s" % {
                    "querystring":urlencode({'source':source, 'from': from_, 'size': size}),
                    "index":index,
                    "type": type_
                    }
        self.get_by_path(path, callback)

    def get_by_path(self, path, callback):
        url = 'http://%(host)s:%(porta)s%(path)s' % {"host": self.host, "porta": self.port, "path": path}
        self.client.fetch(url, callback)