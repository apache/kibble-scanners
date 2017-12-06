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
import uuid

def watsonTone(KibbleBit, body):
    """ Sentiment analysis using IBM Watson """
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
        try:
            rv = requests.post(
                "%s/v3/tone?version=2017-09-21&sentences=false" % KibbleBit.config['watson']['api'],
                headers = headers,
                data = json.dumps(js),
                auth = (KibbleBit.config['watson']['username'], KibbleBit.config['watson']['password'])
            )
            jsout = rv.json()
        except:
            jsout = {} # borked Watson?
        mood = {}
        if 'document_tone' in jsout:
            for tone in jsout['document_tone']['tones']:
                mood[tone['tone_id']] = tone['score']
        else:
            KibbleBit.pprint("Failed to analyze email body.")
        return mood

def azureTone(KibbleBit, body):
    """ Sentiment analysis using Azure Text Analysis API """
    if 'azure' in KibbleBit.config:
        headers = {
            'Content-Type': 'application/json',
            'Ocp-Apim-Subscription-Key': KibbleBit.config['azure']['apikey']
        }
        
        # Crop out quotes
        lines = body.split("\n")
        body = "\n".join([x for x in lines if not x.startswith(">")])
        js = {
            "documents": [
              {
                "language": "en",
                "id": uuid.uuid4(),
                "text": body
              }
            ]
          }
        try:
            rv = requests.post(
                "https://%s.api.cognitive.microsoft.com/text/analytics/v2.0/sentiment" % KibbleBit.config['azure']['location'],
                headers = headers,
                data = json.dumps(js)
            )
            jsout = rv.json()
        except:
            jsout = {} # borked sentiment analysis?
        mood = {}
        if 'documents' in jsout:
            # This is more parred than Watson, so we'll split it into three groups: positive, neutral and negative.
            # Divide into four segments, 0->40%, 25->75% and 60->100%.
            # 0-40 promotes negative, 60-100 promotes positive, and 25-75% promotes neutral.
            # As we don't want to over-represent negative/positive where the results are
            # muddy, the neutral zone is larger than the positive/negative zones by 10%.
            val = jsout['documents'][0]['score']
            mood['negative'] = max(0, ((0.4 - val) * 2.5)) # For 40% and below, use 2½ distance
            mood['positive'] = max(0, ((val-0.6) * 2.5)) # For 60% and above, use 2½ distance
            mood['neutral'] = max(0, 1 - (abs(val - 0.5) * 2)) # Between 25% and 75% use double the distance to middle.
        else:
            KibbleBit.pprint("Failed to analyze email body.")
        return mood
    