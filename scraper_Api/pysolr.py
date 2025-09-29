#!/usr/bin/env python3
"""
Mock pysolr module for testing purposes
"""

class Solr:
    def __init__(self, url=None, auth=None, timeout=None, always_commit=False):
        self.url = url
        self.auth = auth
        self.timeout = timeout
        self.always_commit = always_commit

    def add(self, docs):
        pass

    def delete(self, q):
        pass

    def commit(self, expungeDeletes=False):
        pass

    def search(self, q, **kwargs):
        return []