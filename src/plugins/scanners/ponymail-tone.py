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

"""
This is a Kibble scanner plugin for Apache Pony Mail sources.
"""
import requests
import json
import time
import re
import hashlib
import sys
import datetime
import plugins.utils.jsonapi
import plugins.utils.tone

title = "Tone/Mood Scanner plugin for Apache Pony Mail"
version = "0.1.0"
ROBITS = r"(git|gerrit|jenkins|hudson|builds)@"

def accepts(source):
    """ Test if source matches a Pony Mail archive """
    # If the source equals the plugin name, assume a yes
    if source['type'] == 'ponymail':
        return True
    
    # If it's of type 'mail', check the URL
    if source['type'] == 'mail':
        if re.match(r"(https?://.+)/list\.html\?(.+)@(.+)", source['sourceURL']):
            return True
    
    # Default to not recognizing the source
    return False


def scan(KibbleBit, source):
    # Validate URL first
    url = re.match(r"(https?://.+)/list\.html\?(.+)@(.+)", source['sourceURL'])
    if not url:
        KibbleBit.pprint("Malformed or invalid Pony Mail URL passed to scanner: %s" % source['sourceURL'])
        source['steps']['mail'] = {
            'time': time.time(),
            'status': 'Could not parse Pony Mail URL!',
            'running': False,
            'good': False
        }
        KibbleBit.updateSource(source)
        return
    if not 'watson' in KibbleBit.config:
        KibbleBit.pprint("No Watson/BlueMix creds configured, skipping tone analyzer")
        return
    
    rootURL = re.sub(r"list.html.+", "", source['sourceURL'])
    query = {
            'query': {
                'bool': {
                    'must': [
                        {
                            'term': {
                                'sourceID': source['sourceID']
                            }
                        }
                    ]
                }
            },
            'sort': [{'ts': 'desc'}]
        }
        
    # Get an initial count of commits
    res = KibbleBit.broker.DB.search(
        index=KibbleBit.dbname,
        doc_type="email",
        body = query,
        size = 50
    )
    
    for hit in res['hits']['hits']:
        eml = hit['_source']
        emlurl = "%s/api/email.lua?id=%s" % (rootURL, eml['id'])
        KibbleBit.pprint("Fetching %s" % emlurl)
        rv = requests.get(emlurl).json()
        body = rv['body']
        KibbleBit.pprint("analyzing email")
        if 'mood' not in eml and not re.search(ROBITS, eml['sender']):
            mood = plugins.utils.tone.getTone(KibbleBit, body)
            eml['mood'] = mood
            hm = [0,'unknown']
            for m, s in mood.items():
                if s > hm[0]:
                    hm = [s,m]
            print("Likeliest overall mood: %s" % hm[1])
            KibbleBit.index('email', hit['_id'], eml)
    KibbleBit.pprint("Done with tone analysis")
