#!/usr/bin/env python3.4
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

import re
import hashlib
from dateutil import parser
import time
import requests
import plugins.utils.github

title = "Scanner for GitHub Issues"
version = "0.1.0"

def accepts(source):
    """ Return true if this is a github repo """
    if source['type'] == 'github':
        return True
    if source['type'] == 'git' and re.match(r"https://(?:www\.)?github.com/"):
        return True
    return False

def format_date(d, epoch=False):
    if not d:
        return
    parsed = parser.parse(d)

    if epoch:
        return time.mktime(parsed.timetuple())

    return time.strftime("%Y/%m/%d %H:%M:%S", parsed.timetuple())

def make_hash(source, issue):
    return hashlib.sha224(("%s-%s-%s" % (source['organisation'],
                                         source['sourceID'],
                                         str(issue['id']))).encode('ascii',
                                                                   errors='replace')).hexdigest()

def make_issue(source, issue, people):

    key = str(issue['number'])
    dhash = make_hash(source, issue)

    closed_date = issue.get('closed_at', None)

    owner_email = people[issue['user']['login']]['email']

    issue_closer = owner_email
    if 'closed_by' in issue:
        issue_closer = people[issue['closed_by']['login']]

    return {
        'id': dhash,
        'key': key,
        'organisation': source['organisation'],
        'sourceID': source['sourceID'],
        'url': issue['html_url'],
        'status': issue['state'],
        'created': format_date(issue['created_at'], epoch=True),
        'closed': format_date(closed_date, epoch=True),
        'issueCloser': issue_closer,
        'createdDate': format_date(issue['created_at']),
        'closedDate': format_date(closed_date),
        'changeDate': format_date(closed_date
                                  if closed_date
                                  else issue['updated_at']),
        'assignee': owner_email,
        'issueCreator': owner_email,
        'comments': issue['comments'],
        'title': issue['title']
    }

def make_person(source, issue, raw_person):
    email = raw_person['email']
    if not email:
        email = "%s@invalid.github.com" % issue['user']['login']

    name = raw_person['name']
    if not name:
        name = raw_person['login']

    id = hashlib.sha1(("%s%s" % (source['organisation'],
                                 email)).encode('ascii',
                                                errors='replace')).hexdigest()

    return {'email': email, 'id': id, 'organisation': source['organisation'],
            'name': name}

def status_changed(stored_issue, issue):
    return stored_issue['status'] != issue['status']

def update_issue(KibbleBit, issue):
    KibbleBit.append('issue', issue['id'], issue)

def update_person(KibbleBit, person):
    KibbleBit.append('person', { 'doc': person, 'doc_as_upsert': True})
    

def scan(KibbleBit, source):
    auth=None
    people = {}
    if 'creds' in source:
        KibbleBit.pprint("Using auth for repo %s" % source['sourceURL'])
        creds = source['creds']
        if creds and 'username' in creds:
            auth = (creds['username'], creds['password'])

    try:
        issues = plugins.utils.github.get_all(source, plugins.utils.github.issues,
                                   params={'filter': 'all', 'state':'all'},
                                   auth=auth)
        KibbleBit.pprint("Fetched %s issues for %s" %(str(len(issues)), source['sourceURL']))

        for issue in issues:

            if not issue['user']['login'] in people:
                person = make_person(source, issue, plugins.utils.github.user(issue['user']['url'],
                                                          auth=auth))
                people[issue['user']['login']] = person
                update_person(KibbleBit, person)

            if 'closed_by' in issue and not issue['closed_by']['login'] in people:
                closer = make_person(source, issue, plugins.utils.github.user(issue['closed_by']['url'],
                                                          auth=auth))
                people[issue['closed_by']['login']] = closer
                update_person(KibbleBit, closer)

            doc = make_issue(source, issue, people)
            dhash = doc['id']

            stored_change = None
            if KibbleBit.exists('issue', dhash):
                es_doc = KibbleBit.get('issue', dhash)
                if not status_changed(es_doc, doc):
                    KibbleBit.pprint("change %s seen already and status unchanged. Skipping." % issue['id'])
                    continue

            update_issue(KibbleBit, doc)

    except requests.HTTPError as e:
        # we've likely hit our GH API quota for the hour, so we re-try
        KibbleBit.pprint("HTTP Error, rate limit exceeded?")
        time.sleep(3600)
