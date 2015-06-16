# -*- coding: utf-8 -*-

from tornadoes.models import BulkList

from six.moves.urllib.parse import urlencode
from tornado.escape import json_encode, json_decode
from tornado.ioloop import IOLoop
from tornado.httpclient import AsyncHTTPClient, HTTPRequest
from tornado.concurrent import return_future


class ESConnection(object):

    def __init__(self, host='localhost', port='9200', io_loop=None, protocol='http'):
        self.io_loop = io_loop or IOLoop.instance()
        self.url = "%(protocol)s://%(host)s:%(port)s" % {"protocol": protocol, "host": host, "port": port}
        self.bulk = BulkList()
        self.client = AsyncHTTPClient(self.io_loop)
        self.httprequest_kwargs = {}     # extra kwargs passed to tornado's HTTPRequest class e.g. request_timeout

    def create_path(self, method, **kwargs):
        index = kwargs.pop('index', '_all')
        doc_type = '/%s' % kwargs.pop('type', '')

        parameters = {}
        for param, value in kwargs.items():
            parameters[param] = value

        path = "/%(index)s%(type)s/_%(method)s" % {
            "method": method,
            "index": index,
            "type": doc_type
        }
        if parameters:
            path += '?' + urlencode(parameters)

        return path

    @return_future
    def search(self, callback, **kwargs):
        path = self.create_path("search", **kwargs)
        source = json_encode(kwargs.get('source', {
            "query": {
                "match_all": {}
            }
        }))
        self.post_by_path(path, callback, source)

    def multi_search(self, index, source):
        self.bulk.add(index, source)

    @return_future
    def apply_search(self, callback, params={}):
        path = "/_msearch"
        if params:
            path = "%s?%s" % (path, urlencode(params))
        source = self.bulk.prepare_search()
        self.post_by_path(path, callback, source=source)

    def post_by_path(self, path, callback, source):
        url = '%(url)s%(path)s' % {"url": self.url, "path": path}
        request_http = HTTPRequest(url, method="POST", body=source, **self.httprequest_kwargs)
        self.client.fetch(request=request_http, callback=callback)

    @return_future
    def get_by_path(self, path, callback):
        url = '%(url)s%(path)s' % {"url": self.url, "path": path}
        self.client.fetch(url, callback, **self.httprequest_kwargs)

    @return_future
    def get(self, index, type, uid, callback, parameters=None):
        def to_dict_callback(response):
            source = json_decode(response.body)
            callback(source)
        self.request_document(index, type, uid, callback=to_dict_callback, parameters=parameters)

    @return_future
    def put(self, index, type, uid, contents, parameters=None, callback=None):
        self.request_document(
            index, type, uid, "PUT", body=json_encode(contents),
            parameters=parameters, callback=callback)

    @return_future
    def delete(self, index, type, uid, parameters=None, callback=None):
        self.request_document(index, type, uid, "DELETE", parameters=parameters, callback=callback)

    @return_future
    def count(self, index="_all", type=None, source='', parameters=None, callback=None):
        path = '/{}'.format(index)

        if type:
            path += '/{}'.format(type)

        path += '/_count'

        if parameters:
            path += '?{}'.format(urlencode(parameters or {}))

        if source:
            source = json_encode(source)

        self.post_by_path(path=path, callback=callback, source=source)

    def request_document(self, index, type, uid, method="GET", body=None, parameters=None, callback=None):
        path = '/{index}/{type}/{uid}'.format(**locals())
        url = '%(url)s%(path)s?%(querystring)s' % {
            "url": self.url,
            "path": path,
            "querystring": urlencode(parameters or {})
        }
        request_arguments = dict(self.httprequest_kwargs)
        request_arguments['method'] = method

        if body is not None:
            request_arguments['body'] = body

        request = HTTPRequest(url, **request_arguments)
        self.client.fetch(request, callback)
