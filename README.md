[![Build Status](https://secure.travis-ci.org/globocom/tornado-es.png?branch=master)](https://travis-ci.org/globocom/tornado-es)

Tornado-es
==========

A tornado-powered python library that provides asynchronous access to elasticsearch.

Install
=======

Via pip:

    pip install tornadoes

Versions
========

    ------------------------------------------------------
    | tornadoes version               | Elasticsearch    |
    ------------------------------------------------------
    | 1.*                             | 0.90.*           |
    ------------------------------------------------------
    | 2.*                             | 1.*              |
    ------------------------------------------------------

Usage
=====

Indexing a dummy document:

    $ curl -XPUT 'http://localhost:9200/index_test/typo_test/1' -d '{
        "typo_test" : {
            "name" : "scooby doo"
        }
    }'

Tornado program used to search the document previously indexed:

    # -*- coding: utf-8 -*-

    import json

    import tornado.ioloop
    import tornado.web

    from tornadoes import ESConnection


    class SearchHandler(tornado.web.RequestHandler):

        es_connection = ESConnection("localhost", 9200)

        @tornado.web.asynchronous
        def get(self, indice="index_test", tipo="typo_test"):
            query = {"query": {"match_all": {}}}
            self.es_connection.search(callback=self.callback,
                                      index=indice,
                                      type=tipo,
                                      source=query)

        def callback(self, response):
            self.content_type = 'application/json'
            self.write(json.loads(response.body))
            self.finish()

    application = tornado.web.Application([
        (r"/", SearchHandler),
    ])

    if __name__ == "__main__":
        application.listen(8888)
        tornado.ioloop.IOLoop.instance().start()


Development
===========

Setup your development environment:

    make setup

> *Note: Don't forget to create a virtualenv first*

Run tests:

    make test

> *Note: Make sure ElasticSearch is running on port 9200*


Contributing
============

Fork, patch, test, and send a pull request.
