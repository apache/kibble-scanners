#!env /usr/bin/env python3
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

""" GitHub utility library """
import re
import requests
from json import loads
import time

repo_pattern = re.compile('.*[:/]([^/]+)/([^/]+).git')
issues_api = "https://api.github.com/repos/%s/%s/issues"
traffic_api = "https://api.github.com/repos/%s/%s/traffic"
popular_api = "https://api.github.com/repos/%s/%s/popular"

def issues(source, params={}, auth=None):
    local_params = {'per_page': 100, 'page': 1}
    local_params.update(params)

    repo_user = repo_pattern.findall(source['sourceURL'])[0]
    resp = requests.get(issues_api % repo_user, params=local_params, auth=auth)
    resp.raise_for_status()

    return resp.json()

def views(source, auth=None):
    repo_user = repo_pattern.findall(source['sourceURL'])[0]
    resp = requests.get("%s/views" % (traffic_api % repo_user), auth=auth)
    resp.raise_for_status()
    
    return resp.json()

def clones(source, auth=None):
    repo_user = repo_pattern.findall(source['sourceURL'])[0]
    resp = requests.get("%s/clones" % (traffic_api % repo_user), auth=auth)
    resp.raise_for_status()
    
    return resp.json()

def referrers(source, auth=None):
    repo_user = repo_pattern.findall(source['sourceURL'])[0]
    resp = requests.get("%s/referrers" % (popular_api % repo_user), auth=auth)
    resp.raise_for_status()
    
    return resp.json()

def user(user_url, auth=None):
    resp = requests.get(user_url, auth=auth)
    resp.raise_for_status()

    return resp.json()

def get_all(source, f, params={}, auth=None):
    acc = []
    page = params.get('page', 1)

    while True:
        time.sleep(1.25)
        items = f(source, params=params, auth=auth)
        if not items:
            break

        acc.extend(items)

        page = page + 1
        params.update({"page": page})

    return acc
