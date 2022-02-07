#! /usr/bin/env python2
# -*- coding: utf-8 -*-

import sys
import googleapiclient.http
from httplib2 import Http
from httplib import HTTPResponse
from oauth2client.service_account import ServiceAccountCredentials
from apiclient.discovery import build

scopes = [
        'https://mail.google.com/',
        ]

json_path = sys.argv[1]

user = sys.argv[2]

credentials = ServiceAccountCredentials.from_json_keyfile_name(json_path, scopes)
userId = user
delegated_credentials = credentials.create_delegated(userId)
http_auth = delegated_credentials.authorize(Http())

service = build('gmail', 'v1', http=http_auth)

request = service.users().getProfile(userId=user).execute()

print('\n')
print('Email address: {}'.format(request['emailAddress']))
print('Total threads: {}'.format(request['threadsTotal']))
print('Total email messages: {}'.format(request['messagesTotal']))
