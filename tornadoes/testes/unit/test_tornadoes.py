# -*- coding: utf-8 -*-

import unittest2
import json
from tornadoes import ESConnection
from tornado.testing import AsyncTestCase

class TestESConnection(AsyncTestCase):   
        
    def tratar_resposta_consulta_simples(self, response):
        assert response.code == 200
        resposta = json.loads(response.body)
        assert resposta["hits"]["total"] == 1
        assert resposta["hits"]["hits"][0]["_id"] == u'http://g1.be.globoi.com/noticia/1/fast'
        self.stop()
        
    def tratar_resposta_consulta_especificando_tipo_campo(self, response):
        assert response.code == 200
        resposta = json.loads(response.body)
        assert resposta["hits"]["total"] == 1
        assert resposta["hits"]["hits"][0]["_id"] == u'http://g1.be.globoi.com/noticia/1/fast'
        self.stop()
        
    def test_consulta_simples(self):
        self.es_connection = ESConnection("localhost",  "1980", self.io_loop)
        self.es_connection.get_by_path("/_search?q=_id:http\:\/\/g1.be.globoi.com\/noticia\/1\/fast", self.tratar_resposta_consulta_simples)
        self.wait()
    
    def test_consulta_especificando_tipo_campo(self):
        self.es_connection = ESConnection("localhost",  "1980", self.io_loop)
        self.es_connection.get(self.tratar_resposta_consulta_especificando_tipo_campo, "teste", "http\:\/\/g1.be.globoi.com\/noticia\/1\/fast", "materia", "_id")
        self.wait()