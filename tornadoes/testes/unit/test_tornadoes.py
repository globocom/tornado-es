# -*- coding: utf-8 -*-

import unittest2
import json
from tornadoes import ESConnection

from tornado import escape
from tornado.testing import AsyncTestCase
from tornado.ioloop import IOLoop


class TestESConnection(AsyncTestCase):
    
    def setUp(self):
        self.io_loop = self.get_new_ioloop()
        self.es_connection = ESConnection("localhost", "1980", self.io_loop)
        
    def tearDown(self):
        if (not IOLoop.initialized() or self.io_loop is not IOLoop.instance()):
            self.io_loop.close(all_fds=True)
        super(AsyncTestCase, self).tearDown()        
        
    def tratar_resposta_consulta_simples(self, response):
        assert response.code == 200
        resposta = escape.json_decode(response.body)
        assert resposta["hits"]["total"] == 1
        assert resposta["hits"]["hits"][0]["_id"] == u'http://g1.be.globoi.com/noticia/2/fast'
        self.stop()
        
    def tratar_resposta_consulta_especificando_tipo_campo(self, response):
        resposta = escape.json_decode(response.body)
        assert response.code == 200, resposta
        assert resposta["hits"]["total"] == 1, resposta
        assert resposta["hits"]["hits"][0]["_id"] == u'171171', resposta["hits"]["hits"][0]["_id"]+'\n'+str(resposta)
        self.stop()
        
    def test_consulta_simples(self):
        self.es_connection.get_by_path("/_search?q=_id:http\:\/\/g1.be.globoi.com\/noticia\/2\/fast", self.tratar_resposta_consulta_simples)
        self.wait()

    def test_consulta_especificando_tipo_campo(self):
        self.es_connection.search(callback=self.tratar_resposta_consulta_especificando_tipo_campo,
            source={"query": {"text" : {"ID" : "171171"}}},
            type="materia", index="teste")
        self.wait()

    def verificar_quantidade_de_registros(self, response):
        resposta = escape.json_decode(response.body)
        assert response.code == 200, "response.code != 200\n" + str(resposta)
        assert resposta["hits"]["total"] == 28
        self.stop()
    
    def test_consulta_todos_os_registros(self):
        self.es_connection.search(self.verificar_quantidade_de_registros)
        self.wait()
        
    def verificar_busca_indice_especifico(self, response):
        resposta = escape.json_decode(response.body)
        assert response.code == 200, "response.code != 200\n" + resposta
        assert resposta["hits"]["total"] == 14
        self.stop()
    
    def test_busca_indice_especifico(self):
        self.es_connection.search(callback=self.verificar_busca_indice_especifico, index="outroteste")
        self.wait()
        
    def verificar_busca_tipo_especifico(self, response):
        resposta = escape.json_decode(response.body)
        assert response.code == 200, "response.code != 200\n" + str(resposta)
        assert resposta["hits"]["total"] == 2
        self.stop()
    
    def test_busca_tipo_especifico(self):
        self.es_connection.search(self.verificar_busca_tipo_especifico, type='galeria')
        self.wait()
