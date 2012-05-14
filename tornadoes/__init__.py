# -*- coding: utf-8 -*-

from tornado.httpclient import AsyncHTTPClient
from tornado.ioloop import IOLoop

class ESConnection:
    
    def __init__(self, host='', port= '9200', io_loop=None):
        self.io_loop = io_loop or IOLoop.instance()
        self.host = host
        self.port = port
        self.client = AsyncHTTPClient(self.io_loop)
        
    def get(self, callback, **kwargs):
        index = kwargs.get('index', '_all')
        type = '/' + kwargs.get('type') if kwargs.has_key('type') else ''
        field = kwargs.get('field','_all') + ':'
        value = kwargs.get('value', '')
        size = kwargs.get('size', 10)
        page = kwargs.get('page', 1)
        begin = (page-1)*size        
        
        path = "/%(index)s%(type)s/_search?q=%(field)s%(value)s&from=%(begin)d&size=%(size)d" % {"index": index, "type": type, "field": field, 
                                                                                                  "value": value, "begin": begin, "size":size}
        
        self.get_by_path(path, callback)
        
    def get_by_path(self, path, callback):
        url = 'http://%(host)s:%(porta)s%(path)s' % {"host": self.host, "porta": self.port, "path": path}
        self.client.fetch(url, callback)