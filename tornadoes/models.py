# -*- coding: utf-8 -*-

import threading

from tornado.escape import json_encode


class BulkList(object):

    def __init__(self):
        self.lock = threading.RLock()
        with self.lock:
            self.bulk_list = []

    def add(self, index, source):
        with self.lock:
            command = {"index": index} if index else {}
            source = "%s\n%s" % (json_encode(command), json_encode(source))
            self.bulk_list.append(source)

    def prepare_search(self):
        with self.lock:
            source = "\n".join(self.bulk_list) + "\n"
            self.bulk_list = []
            return source
