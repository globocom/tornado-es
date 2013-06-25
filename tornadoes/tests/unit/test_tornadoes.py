# -*- coding: utf-8 -*-

from tornadoes import ESConnection

from tornado import escape
from tornado.testing import AsyncTestCase
from tornado.ioloop import IOLoop


class TestESConnection(AsyncTestCase):

    def setUp(self):
        self.io_loop = self.get_new_ioloop()
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
                                  source={"query": {"text": {"ID": "171171"}}},
                                  type="materia", index="teste")

        response = self._verify_status_code_and_return_response()
        self.assertEqual(response["hits"]["total"], 1)
        self.assertEqual(response["hits"]["hits"][0]["_id"], u'171171')

    def test_search_all_entries(self):
        self.es_connection.search(self.stop)
        response = self._verify_status_code_and_return_response()
        self.assertEqual(response["hits"]["total"], 28)

    def test_search_specific_index(self):
        self.es_connection.search(callback=self.stop, index="outroteste")
        response = self._verify_status_code_and_return_response()
        self.assertEqual(response["hits"]["total"], 14)

    def test_search_apecific_type(self):
        self.es_connection.search(self.stop, type='galeria')
        response = self._verify_status_code_and_return_response()
        self.assertEqual(response["hits"]["total"], 2)

    def test_should_access_specific_documento(self):
        self.es_connection.get(index="teste", type="materia", uid="171171", callback=self.stop)
        response = self.wait()
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
        source = {"query": {"text": {"_id": "171171"}}}
        self.es_connection.multi_search(index="teste", source=source)
        source = {"query": {"text": {"_id": "101010"}}}
        self.es_connection.multi_search(index="neverEndIndex", source=source)

        self.es_connection.apply_search(callback=self.stop)

    def _verify_status_code_and_return_response(self):
        response = self.wait()
        self.assertEqual(response.code, 200, "Wrong response code.")
        response = escape.json_decode(response.body)
        return response
