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
This is a Kibble JSON API plugin.
"""
import requests
import json
import time
import re

def getJSON(url, cookie = None, auth = None):
    headers = {
        "Content-type": "application/json",
        "Accept": "*/*"
    }
    if auth:
        xcreds = creds.encode(encoding='ascii', errors='replace')
        auth = base64.encodebytes(xcreds).decode('ascii', errors='replace').replace("\n", '')
        headers["Authorization"] = "Basic %s" % auth
    if cookie:
        headers["Cookie"] = cookie
    rv = requests.get(url, headers = headers)
    js = rv.json()
    return js

    