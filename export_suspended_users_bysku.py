#!/usr/bin/env python
# coding=utf-8
import datetime
import json
import os
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage
import urllib
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from httplib2 import Http
from httplib import HTTPResponse
#from http.client import HTTPResponse Python3
from oauth2client.service_account import ServiceAccountCredentials
from apiclient.discovery import build
#from googleapiclient.discovery import build Python3

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

SCOPES = ['https://www.googleapis.com/auth/admin.directory.user', 'https://www.googleapis.com/auth/apps.licensing', 'https://www.googleapis.com/auth/admin.reports.audit.readonly', 'https://mail.google.com/']
QUERY = 'isSuspended=true' # query list https://developers.google.com/admin-sdk/directory/v1/guides/search-users
CLIENT_SECRET_FILE = '/Users/lonix/GAM/noovle/client_secrets.json'
APPLICATION_NAME = 'Print suspended users'
CUSTOMER_ID = 'INSERT_CUSTOMER_ID'  # your unique customer ID https://support.google.com/cloudidentity/answer/10070793?hl=en
CUSTOMER_JSON = CUSTOMER_ID + '.json' # this JSON will be created inside the folder ~/.credential
SKU_ID = 'INSERT_SKU_TO_BE_FILTER'  #  SKU List  https://developers.google.com/admin-sdk/licensing/v1/how-tos/products
MAIL_FROM = 'sender@example.com'
MAIL_TO = 'recipient1@example.com'
MAIL_CC = 'recipient2@example.com'


def format_date(date_str):
    converted = datetime.datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%S.%fZ')
    converted = converted.strftime("%d-%m-%Y")
    return converted

def get_credentials():
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   CUSTOMER_JSON)

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
            print('Storing credentials to ' + credential_path)
    return credentials

def main():
    query = QUERY
    query_body = urllib.quote_plus(query)
    credentials = get_credentials()
    http_auth = credentials.authorize(Http())
    service = build('admin', 'directory_v1', http=http_auth)
    users_list = service.users().list(customer=CUSTOMER_ID, query=query).execute()
    users_array = []
    enterprise_users = []
    for item in users_list['users']:
        users_array.append([item['primaryEmail'],item['orgUnitPath']])
    while 'nextPageToken' in users_list:
        users_list = service.users().list(customer=CUSTOMER_ID, pageToken = users_list['nextPageToken'], query=query).execute()
        for item in users_list['users']:
            users_array.append([item['primaryEmail'],item['orgUnitPath']])
    print ("Recovering suspended users with the required license ...")
    for user in users_array:
        print ('# ' + user[0] + ' | Org : ' + user[1])
        service = build('licensing', 'v1', http=http_auth)
        try:
            license = service.licenseAssignments().get(productId="Google-Apps", skuId=SKU_ID, userId=user[0]).execute()
            enterprise_users.append([license['userId'],user[1]])

        except:
            continue
    #if flags in users_array
    print ("I'm getting ready to print users and suspension date ...")
    service = build('admin', 'reports_v1', http=http_auth)
    suspended_users = service.activities().list(userKey='all', applicationName='admin', eventName='SUSPEND_USER').execute()
    to_assign = []
    for user in enterprise_users:
        for item in suspended_users['items']:
            if item['events'][0]['parameters'][0]['value'] == user[0]:
                to_assign.append('<tr><td>' + user[0] +  "</td><td>&emsp;</td><td>" + format_date(item['id']['time']) + "<td>&emsp;</td><td>"  + user[1] +  '</td></tr>')
                print ('# ' + user[0] + ' | Suspension Date : ' + format_date(item['id']['time']))
                break

    mail_body = "</td></tr>".join(to_assign)
    mail_body = "<table><tr><th style='text-align:left;'>User mail</th><th>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</th><th style='text-align:left;'>Suspension Date</th></b><th>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</th><th style='text-align:left;'>orgUnitPath</th></b></tr>" + mail_body + '</table><br>'

    service = build('gmail', 'v1', http=http_auth)

    message = MIMEMultipart()
    message['to'] = MAIL_TO
    message['from'] = MAIL_FROM
    message['cc'] = MAIL_CC
    message['subject'] = 'REPORT - Suspended users'
    msg = MIMEText(mail_body,'html')
    message.attach(msg)
    raw = base64.urlsafe_b64encode(message.as_string())

    payload = {
            "raw": raw
            }

    service.users().messages().send(userId='me', body=payload).execute()

    print ("Mail sent successfully to: " + MAIL_TO)

if __name__ == "__main__":
    main()
