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

""" This is the Kibble git utility plugin """

import os
import sys
import subprocess
import re

def defaultBranch(source, datapath):
    """ Tries to figure out what the main branch of a repo is """
    branch = ""
    try:
        branch = subprocess.check_output('cd %s && git rev-parse --abbrev-ref master' % datapath,  shell = True, stderr=subprocess.DEVNULL).decode('ascii', 'replace').strip().strip("* ")
    except:
        try:
            branch = subprocess.check_output('cd %s & git rev-parse --abbrev-ref trunk' % datapath,  shell = True, stderr=subprocess.DEVNULL).decode('ascii', 'replace').strip().strip("* ")
        except:
            try:
                inp = subprocess.check_output("cd %s && git branch -a | awk -F ' +' '! /\(no branch\)/ {print $2}'" % datapath,  shell = True, stderr=subprocess.DEVNULL).decode('ascii', 'replace').split()
                if len(inp) > 0:
                    for b in inp:
                        if b.find("detached") == -1:
                            branch = str(b.replace("remotes/origin/", "", 1))
                            if branch == 'master':
                                break
            except:
                branch = ""

    # If still not found, resort to a remote listing
    if branch == "" and repo:
        inp = subprocess.check_output("cd %s && git ls-remote --heads %s" % (datapath, source['sourceURL']),  shell = True, stderr=subprocess.DEVNULL).decode('ascii', 'replace').split()
        if len(inp) > 0:
            for remote in inp:
                m = re.match(r"[a-f0-9]+\s+refs/heads/(?:remotes/)?(.+)", remote)
                if m:
                    branch = m.group(1)
                    break
    return branch.replace("remotes/", "", 1)