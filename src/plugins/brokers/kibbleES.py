#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
 #the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json
import elasticsearch
import elasticsearch.helpers
import threading
import sys

# This is redundant, refactor later?
def pprint(string, err = False):
    line = "[core]: %s" % (string)
    if err:
        sys.stderr.write(line + "\n")
    else:
        print(line)

class KibbleBit:
    """ KibbleBit class with direct ElasticSearch access """
    
    def __init__(self, broker, organisation, tid):
        self.config = broker.config
        self.organisation = organisation
        self.broker = broker
        self.json_queue = []
        self.queueMax = 250 # Entries to keep before bulk pushing
        self.pluginname = ""
        self.tid = tid
    
    def __del__(self):
        """ On unload/delete, push the last chunks of data to ES """
        if self.json_queue:
            self.bulk()
            
    def pprint(self,  string, err = False):
        line = "[thread#%i:%s]: %s" % (self.tid, self.pluginname, string)
        if err:
            sys.stderr.write(line + "\n")
        else:
            print(line)
        
    def updateSource(self, source):
        """ Updates a source document, usually with a status update """
        self.broker.DB.index(index=self.broker.config['elasticsearch']['database'],
                    doc_type="source",
                    id=source['sourceID'],
                    body = source
        )
        
    def get(self, doctype, docid):
        """ Fetches a document from the DB """
        doc = self.broker.DB.get(index=self.broker.config['elasticsearch']['database'], doc_type=doctype, id = docid)
        if doc:
            return doc['_source']
        return None
    
    def exists(self, doctype, docid):
        """ Checks whether a document already exists or not """
        return self.broker.DB.exists(index=self.broker.config['elasticsearch']['database'], doc_type=doctype, id = docid)
    
    def index(self, doctype, docid, document):
        """ Adds a new document to the index """
        self.broker.DB.index(index=self.broker.config['elasticsearch']['database'], doc_type = doctype, id = docid, body = document)
        
    def append(self, t, doc):
        """ Append a document to the bulk push queue """
        if not 'id' in doc:
            sys.stderr.write("No doc ID specified!\n")
            return
        doc['doctype'] = t
        self.json_queue.append(doc)
        # If we've crossed the bulk limit, do a push
        if len(self.json_queue) > self.queueMax:
            pprint("Bulk push forced")
            self.bulk()
        
    def bulk(self):
        """ Push pending JSON objects in the queue to ES"""
        xjson = self.json_queue
        js_arr = []
        self.json_queue = []
        for entry in xjson:
            js = entry
            doc = js
            if js.get('upsert'):
                doc = {
                    'doc_as_upsert': True,
                    'doc': js
                }
            js['@version'] = 1
            js_arr.append({
                '_op_type': 'index',
                '_consistency': 'quorum',
                '_index': self.broker.config['elasticsearch']['database'],
                '_type': js['doctype'],
                '_id': js['id'],
                'doc': doc,
                '_source': js
            })
        try:
            elasticsearch.helpers.bulk(self.broker.DB, js_arr)
        except Exception as err:
            pprint("Warning: Could not bulk insert: %s" % err)
        

class KibbleOrganisation:
    """ KibbleOrg with direct ElasticSearch access """
    def __init__(self, broker, org):
        """ Init an org, set up ElasticSearch for KibbleBits later on """
        
        self.broker = broker
        self.id = org
    
    def sources(self, sourceType = None, view = None):
        """ Get all sources or sources of a specific type for an org """
        s = []
        # Search for all sources of this organisation
        mustArray = [{
                        'term': {
                            'organisation': self.id
                        }
                    }
                    ]
        if view:
            res = self.broker.DB.get(
                index=self.broker.config['elasticsearch']['database'],
                doc_type="view",
                id = view
            )
            if res:
                mustArray.append({
                                'terms': {
                                    'sourceID': res['_source']['sourceList']
                                }
                            })
        # If we want a specific source type, amend the search criteria
        if sourceType:
            mustArray.append({
                                'term': {
                                    'type': sourceType
                                }
                            })
        # Run the search, fetch all results, 9999 max. TODO: Scroll???
        res = self.broker.DB.search(
            index=self.broker.config['elasticsearch']['database'],
            doc_type="source",
            size = 9999,
            body = {
                'query': {
                    'bool': {
                        'must': mustArray
                    }
                },
                'sort': {
                    'sourceURL': 'asc'
                }
            }
        )
    
        for hit in res['hits']['hits']:
            if sourceType == None or hit['_source']['type'] == sourceType:
                s.append(hit['_source'])
        return s

""" Master Kibble Broker Class for direct ElasticSearch access """
class Broker:
    def __init__(self, config):
        es_config = config['elasticsearch']
        auth = None
        if 'user' in es_config:
            auth = (es_config['user'], es_config['password'])
        pprint("Connecting to ElasticSearch database at %s:%i..." % (es_config['hostname'], es_config.get('port', 9200)))
        es = elasticsearch.Elasticsearch([{
            'host': es_config['hostname'],
            'port': int(es_config.get('port', 9200)),
            'use_ssl': es_config.get('ssl', False),
            'verify_certs': False,
            'url_prefix': es_config.get('uri', ''),
            'http_auth': auth
        }],
            max_retries=5,
            retry_on_timeout=True
        )
        pprint("Connected!")
        self.DB = es
        self.config = config
        self.bitClass = KibbleBit
        
        if not es.indices.exists(index = es_config['database']):
            sys.stderr.write("Could not find database %s in ElasticSearch!\n" % es_config['database'])
            sys.exit(-1)
    
    def organisations(self):
        """ Return a list of all organisations """
        orgs = []
        
        # Run the search, fetch all orgs, 9999 max. TODO: Scroll???
        res = self.DB.search(
            index=self.config['elasticsearch']['database'],
            doc_type="organisation",
            size = 9999,
            body = {
                'query': {
                    'match_all': {}
                }
            }
        )
    
        for hit in res['hits']['hits']:
            org = hit['_source']['id']
            orgClass = KibbleOrganisation(self, org)
            yield orgClass
        
    
