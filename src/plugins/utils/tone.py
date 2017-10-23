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
This is an experimental tone analyzer plugin for using Watson/BlueMix for
analyzing the mood of email on a list. This requires a Watson account
and a watson section in config.yaml, as such:

watson:
    username: $user
    password: $pass
    api:      https://$something.watsonplatform.net/tone-analyzer/api
    
Currently only pony mail is supported. more to come.
"""

import time
import datetime
import re
import json
import hashlib
import requests
import json

def getTone(KibbleBit, body):
    if 'watson' in KibbleBit.config:
        headers = {
            'Content-Type': 'application/json'
        }
        
        # Crop out quotes
        lines = body.split("\n")
        body = "\n".join([x for x in lines if not x.startswith(">")])
        
        js = {
            'text': body
        }
        rv = requests.post(
            "%s/v3/tone?version=2017-09-21&sentences=false" % KibbleBit.config['watson']['api'],
            headers = headers,
            data = json.dumps(js),
            auth = (KibbleBit.config['watson']['username'], KibbleBit.config['watson']['password'])
        )
        mood = {}
        jsout = rv.json()
        if 'document_tone' in jsout:
            for tone in jsout['document_tone']['tones']:
                mood[tone['tone_id']] = tone['score']
        else:
            KibbleBit.pprint("Failed to analyze email body.")
        return mood

