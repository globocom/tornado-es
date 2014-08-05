# -*- coding: utf-8 -*-

from uuid import uuid4

from tornadoes import ESConnection
from tornado import escape
from tornado.testing import AsyncTestCase, gen_test
from tornado.ioloop import IOLoop


class TestESConnection(AsyncTestCase):

    def setUp(self):
        super(TestESConnection, self).setUp()
        self.es_connection = ESConnection("localhost", "9200", self.io_loop)

    def tearDown(self):
        if (not IOLoop.initialized() or self.io_loop is not IOLoop.instance()):
            self.io_loop.close(all_fds=True)
        super(AsyncTestCase, self).tearDown()

    def test_simple_search(self):
        self.es_connection.get_by_path("/_search?q=_id:http\:\/\/localhost\/noticia\/2\/fast", self.stop)
        response = self._verify_status_code_and_return_response()
        self.assertEqual(response["hits"]["total"], 1)
        self.assertEqual(response["hits"]["hits"][0]["_id"], u'http://localhost/noticia/2/fast')

    def test_search_for_specific_type_with_query(self):
        self.es_connection.search(callback=self.stop,
                                  source={"query": {"term": {"ID": "171171"}}},
                                  type="materia", index="teste")

        response = self._verify_status_code_and_return_response()
        self.assertEqual(response["hits"]["total"], 1)
        self.assertEqual(response["hits"]["hits"][0]["_id"], u'171171')

    def test_search_specific_index(self):
        self.es_connection.search(callback=self.stop, index="outroteste")
        response = self._verify_status_code_and_return_response()
        self.assertEqual(response["hits"]["total"], 14)

    def test_search_apecific_type(self):
        self.es_connection.search(self.stop, type='galeria')
        response = self._verify_status_code_and_return_response()
        self.assertEqual(response["hits"]["total"], 2)

    def test_should_access_specific_document(self):
        self.es_connection.get(index="teste", type="materia", uid="171171", callback=self.stop)
        response = self.wait()["_source"]
        self.assertEqual(response['Portal'], "G1")
        self.assertEqual(response['Macrotema'], "Noticias")

    def test_should_accumulate_searches_before_search(self):
        source = {"query": {"text": {"_id": "171171"}}}
        self.es_connection.multi_search("teste", source=source)
        source = {"query": {"text": {"body": "multisearch"}}}
        self.es_connection.multi_search("neverEndIndex", source=source)

        self.assertListEqual(['{"index": "teste"}\n{"query": {"text": {"_id": "171171"}}}',
                              '{"index": "neverEndIndex"}\n{"query": {"text": {"body": "multisearch"}}}'
                              ], self.es_connection.bulk.bulk_list)

    def test_should_generate_empty_header_with_no_index_specified(self):
        source = {"query": {"text": {"_id": "171171"}}}
        self.es_connection.multi_search(index=None, source=source)
        source = {"query": {"text": {"body": "multisearch"}}}
        self.es_connection.multi_search(index=None, source=source)

        self.assertListEqual(['{}\n{"query": {"text": {"_id": "171171"}}}',
                              '{}\n{"query": {"text": {"body": "multisearch"}}}'
                              ], self.es_connection.bulk.bulk_list)

    def test_should_make_two_searches(self):
        self._make_multisearch()
        response = self._verify_status_code_and_return_response()
        self.assertEqual(response['responses'][0]['hits']['hits'][0]['_id'], "171171")
        self.assertFalse("hits" in response['responses'][1])

    def test_should_clean_search_list_after_search(self):
        self._make_multisearch()
        self.wait()
        self.assertListEqual([], self.es_connection.bulk.bulk_list)

    def _make_multisearch(self):
        source = {"query": {"term": {"_id": "171171"}}}
        self.es_connection.multi_search(index="teste", source=source)
        source = {"query": {"term": {"_id": "101010"}}}
        self.es_connection.multi_search(index="neverEndIndex", source=source)

        self.es_connection.apply_search(callback=self.stop)

    def _verify_status_code_and_return_response(self):
        response = self.wait()
        return self._verify_response_and_returns_dict(response)

    def _verify_response_and_returns_dict(self, response):
        self.assertTrue(response.code in [200, 201], "Wrong response code: %d." % response.code)
        response = escape.json_decode(response.body)
        return response

    def test_can_put_and_delete_document(self):
        try:
            doc_id = str(uuid4())

            self.es_connection.put("test", "document", doc_id, {
                "test": "document",
                "other": "property"
            }, parameters={'refresh': True}, callback=self.stop)

            response = self.wait()
            response_dict = self._verify_response_and_returns_dict(response)
            self.assertEqual(response_dict['_index'], 'test')
            self.assertEqual(response_dict['_type'], 'document')
            self.assertEqual(response_dict['_id'], doc_id)
            self.assertIn('refresh=True', response.request.url)
        finally:
            self.es_connection.delete("test", "document", doc_id,
                                      parameters={'refresh': True}, callback=self.stop)
            response = self._verify_status_code_and_return_response()

            self.assertTrue(response['found'])
            self.assertEqual(response['_index'], 'test')
            self.assertEqual(response['_type'], 'document')
            self.assertEqual(response['_id'], doc_id)

    def test_count_specific_index(self):
        self.es_connection.count(callback=self.stop, index="outroteste")
        response = self._verify_status_code_and_return_response()
        self.assertEqual(response["count"], 14)

    def test_count_specific_type(self):
        self.es_connection.count(callback=self.stop, type='galeria')
        response = self._verify_status_code_and_return_response()
        self.assertEqual(response["count"], 2)

    def test_count_specific_query(self):
        source = {"query": {"term": {"_id": "171171"}}}
        self.es_connection.count(callback=self.stop, source=source)
        response = self._verify_status_code_and_return_response()
        self.assertEqual(response["count"], 1)

    def test_count_specific_query_with_parameters(self):
        source = {"query": {"term": {"_id": "171171"}}}
        parameters = {'refresh': True}
        self.es_connection.count(callback=self.stop, source=source, parameters=parameters)
        response = self.wait()
        response_dict = self._verify_response_and_returns_dict(response)
        self.assertEqual(response_dict["count"], 1)
        self.assertTrue(response.request.url.endswith('_count?refresh=True'))

    def test_count_specific_query_with_many_parameters(self):
        source = {"query": {"term": {"_id": "171171"}}}
        parameters = {'df': '_id', 'test': True}
        self.es_connection.count(callback=self.stop, source=source, parameters=parameters)
        response = self.wait()
        response_dict = self._verify_response_and_returns_dict(response)
        self.assertEqual(response_dict["count"], 1)
        self.assertTrue('df=_id' in response.request.url)
        self.assertTrue('test=True' in response.request.url)


class TestESConnectionWithTornadoGen(AsyncTestCase):

    def setUp(self):
        super(TestESConnectionWithTornadoGen, self).setUp()
        self.es_connection = ESConnection("localhost", "9200", self.io_loop)

    def tearDown(self):
        if (not IOLoop.initialized() or self.io_loop is not IOLoop.instance()):
            self.io_loop.close(all_fds=True)
        super(AsyncTestCase, self).tearDown()

    @gen_test
    def test_simple_search(self):
        response = yield self.es_connection.get_by_path("/_search?q=_id:http\:\/\/localhost\/noticia\/2\/fast", self.stop)

        response = self._verify_status_code_and_return_response(response)

        self.assertEqual(response["hits"]["total"], 1)
        self.assertEqual(response["hits"]["hits"][0]["_id"], u'http://localhost/noticia/2/fast')

    @gen_test
    def test_search_for_specific_type_with_query(self):
        response = yield self.es_connection.search(
            source={"query": {"term": {"ID": "171171"}}},
            type="materia", index="teste"
        )

        response = self._verify_status_code_and_return_response(response)
        self.assertEqual(response["hits"]["total"], 1)
        self.assertEqual(response["hits"]["hits"][0]["_id"], u'171171')

    @gen_test
    def test_search_specific_index(self):
        response = yield self.es_connection.search(index="outroteste")
        response = self._verify_status_code_and_return_response(response)
        self.assertEqual(response["hits"]["total"], 14)

    @gen_test
    def test_search_apecific_type(self):
        response = yield self.es_connection.search(type='galeria')
        response = self._verify_status_code_and_return_response(response)
        self.assertEqual(response["hits"]["total"], 2)

    @gen_test
    def test_should_access_specific_document_using_tornado_gen(self):
        response = yield self.es_connection.get(index="teste", type="materia", uid="171171")
        response = response["_source"]
        self.assertEqual(response['Portal'], "G1")
        self.assertEqual(response['Macrotema'], "Noticias")

    @gen_test
    def test_should_make_two_searches(self):
        self._make_multisearch()
        response = yield self.es_connection.apply_search()
        response = self._verify_status_code_and_return_response(response)

        self.assertEqual(response['responses'][0]['hits']['hits'][0]['_id'], "171171")
        self.assertFalse("hits" in response['responses'][1])

    @gen_test
    def test_should_clean_search_list_after_search(self):
        self._make_multisearch()
        response = yield self.es_connection.apply_search()
        response = self._verify_status_code_and_return_response(response)

        self.assertListEqual([], self.es_connection.bulk.bulk_list)

    @gen_test
    def test_can_put_and_delete_document(self):
        try:
            doc_id = str(uuid4())

            response = yield self.es_connection.put("test", "document", doc_id, {
                "test": "document",
                "other": "property"
            }, parameters={'refresh': True})

            response_dict = self._verify_status_code_and_return_response(response)
            self.assertEqual(response_dict['_index'], 'test')
            self.assertEqual(response_dict['_type'], 'document')
            self.assertEqual(response_dict['_id'], doc_id)
            self.assertIn('refresh=True', response.request.url)
        finally:
            response = yield self.es_connection.delete("test", "document", doc_id,
                                                       parameters={'refresh': True})
            response = self._verify_status_code_and_return_response(response)

            self.assertTrue(response['found'])
            self.assertEqual(response['_index'], 'test')
            self.assertEqual(response['_type'], 'document')
            self.assertEqual(response['_id'], doc_id)

    @gen_test
    def test_count_specific_index(self):
        response = yield self.es_connection.count(index="outroteste")
        self.assertCount(response, 14)

    @gen_test
    def test_count_specific_type(self):
        response = yield self.es_connection.count(type='galeria')
        self.assertCount(response, 2)

    @gen_test
    def test_count_specific_query(self):
        source = {"query": {"term": {"_id": "171171"}}}
        response = yield self.es_connection.count(source=source)
        self.assertCount(response, 1)

    @gen_test
    def test_count_specific_query_with_parameters(self):
        source = {"query": {"term": {"_id": "171171"}}}
        parameters = {'refresh': True}
        response = yield self.es_connection.count(callback=self.stop, source=source, parameters=parameters)
        self.assertCount(response, 1)
        self.assertTrue(response.request.url.endswith('_count?refresh=True'))

    @gen_test
    def test_count_specific_query_with_many_parameters(self):
        source = {"query": {"term": {"_id": "171171"}}}
        parameters = {'df': '_id', 'test': True}
        response = yield self.es_connection.count(callback=self.stop, source=source, parameters=parameters)
        self.assertCount(response, 1)
        self.assertTrue('df=_id' in response.request.url)
        self.assertTrue('test=True' in response.request.url)

    def assertCount(self, response, count):
        response_dict = self._verify_status_code_and_return_response(response)
        self.assertEqual(response_dict["count"], count)

    def _make_multisearch(self):
        source = {"query": {"term": {"_id": "171171"}}}
        self.es_connection.multi_search(index="teste", source=source)
        source = {"query": {"term": {"_id": "101010"}}}
        self.es_connection.multi_search(index="neverEndIndex", source=source)

    def _verify_status_code_and_return_response(self, response):
        self.assertTrue(response.code in [200, 201], "Wrong response code: %d." % response.code)
        response = escape.json_decode(response.body)
        return response
