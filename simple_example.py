#!/usr/bin/env python

EXPORT_TYPE="multi" # 'multi' or 'single' supported
POLL_INTERVAL=5 #wait X seconds between each status check. Keep above 30 seconds to avoid being blocked by firewalls
MAX_VERIFY_HOURS=24 # number of hours after which to cancel a job

# *EXPERIMENTAL*
# Url which will be POST'd to on job completion (alternative to Polling)
# This requires a *valid* URL which accepts HTTP POST.
# The payload will be in the same json format as a 'Status' request response
CALLBACK_URL=""

import sys, os, re
import argparse
import requests
import json
import time

def valid_file(parser, arg):
    if not os.path.exists(arg):
        parser.error("The file %s does not exist!" % arg)
    else:
        return arg

def handle_upload(ApiUrl, Token, ExportType, File, Notify):
    Headers= {'x-authorization': Token}
    Data = {}
    if MAX_VERIFY_HOURS != None and MAX_VERIFY_HOURS > 1:
        Data['max_verify_hours'] = str(MAX_VERIFY_HOURS)
    if CALLBACK_URL != None and CALLBACK_URL != "":
        Data['callback_url'] = CALLBACK_URL
    if CALLBACK_URL != None and CALLBACK_URL != "":
        Data['callback_url'] = CALLBACK_URL
    if Notify != None and Notify != "":
        Data['notify_email'] = Notify
    Data['export_type'] = ExportType
    with open(File, 'rb') as f:
        Response = requests.post(ApiUrl, data=Data, files={'file': f}, headers=Headers)
        # Handle response headers
        Status = Response.status_code
        if Status == 202:
            return json.loads(Response.text)['jobs']
        else:
            Response.raise_for_status()

def handle_downloads(Token, Jobs):
    for Job in Jobs:
        print "Job: %s" % json.dumps(Job, indent=4, separators=(',', ': '))
        DownloadUrl = wait_until_ready(Token, Job)
        Filename = do_download(Token, DownloadUrl)
        print "DOWNLOAD: %s completed, saved as %s" % (Job['name'], Filename)
        DeleteResult = do_delete(Token, Job['status_url'])
        print "Delete response: %s" % DeleteResult

def wait_until_ready(Token, Job):
    Headers= {'x-authorization': Token}
    Response = requests.get(Job['status_url'], headers=Headers)
    # Handle response headers
    Status = Response.status_code
    if Status == 200:
        Resp = json.loads(Response.text)
        print Response.text
        if Resp['status'] in ['pending', 'active']:
            print "waiting...."
            time.sleep(POLL_INTERVAL)
            return wait_until_ready(Token, Job)
        elif Resp['status'] == 'completed':
            print "returning %s" % Resp['download_url']
            return Resp['download_url']
        else:
            raise ValueError("Unknown status %s" % Response.text)
    else:
        Response.raise_for_status(Response.text)

def do_download(Token, DownloadUrl):
    Headers= {'x-authorization': Token}
    r = requests.get(DownloadUrl, headers=Headers, stream=True)
    Filename = re.findall('filename="([^"]*)',r.headers['content-disposition'])[0]
    Target = "/tmp/%s" % Filename
    with open(Target, "wb") as fd:
        for chunk in r.iter_content(chunk_size=128):
            fd.write(chunk)
    return Target

def do_delete(Token, DeleteUrl):
    Headers= {'x-authorization': Token}
    r = requests.delete(DeleteUrl, headers=Headers)
    return r.text

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Upload and then download a file from ListCertified')
    parser.add_argument('-u', dest='url', required=False,
                        help="Bulk REST API Endpoint. Should end in 'bulk'", type=str)
    parser.add_argument('-t', dest='token', required=True,
                        help='The Auth Token to use', type=str)
    parser.add_argument('-f', dest='file', required=True,
                        help='The file to upload',
                        type=lambda x: valid_file(parser, x))
    parser.add_argument('-n', dest='notify', required=False,
                        help='Email Address to notify when Job is completed', type=str)
    parser.add_argument('-e', dest='exporttype', required=False, default="multi",
                        help="May be 'multi' or 'single'. Defaults to 'multi'", type=str)

    args = parser.parse_args()

    # When the file is uploaded it may be split into multiple jobs,
    # so note that Jobs is a list of one or more jobs
    Jobs = handle_upload(args.url, args.token, args.exporttype, args.file, args.notify)
    handle_downloads(args.token, Jobs)

