# -*- coding: utf-8 -*-

from tornado.httpclient import AsyncHTTPClient
from tornado.ioloop import IOLoop

class ESConnection:
    
    def __init__(self, host='', port= '9200', io_loop=None):
        self.io_loop = io_loop or IOLoop.instance()
        self.host = host
        self.port = port
        self.client = AsyncHTTPClient(self.io_loop)
        
    def get(self, callback, indice, valor, tipo=None, campo=None):
        tipo_query = "/%1s" % tipo if tipo else ""
        campo_query = "%1s:" %campo if campo else "_all:"
        
        path = "/%(indice)s%(tipo)s/_search?q=%(campo)s%(valor)s" % {"indice": indice, "tipo": tipo_query, "campo": campo_query, "valor": valor}
        self.get_by_path(path, callback)
        
    def get_by_path(self, path, callback):
        url = 'http://%(host)s:%(porta)s%(path)s' % {"host": self.host, "porta": self.port, "path": path}
        self.client.fetch(url, callback)