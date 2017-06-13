import io, csv, email, json, re, base64
from email import header
from email.utils import getaddresses

from bs4 import BeautifulSoup

import arxiv
import chardet
from chardet.universaldetector import UniversalDetector
import requests
import xmltodict
from TwitterAPI import TwitterAPI, TwitterRestPager

mail = json.load(open('debug-mail-2.json'))
subject = None
try:
    header = {}
    for item in mail['payload']['headers']:
        header[item['name'].lower()] = item['value']
    subject = header['subject']
except:
    pass

parts = {}
def parse_part(big_part):
    def decode_and_add(part):
        data = part['body']['data']
        decoded = base64.b64decode(data.replace('-','+').replace('_','/'))
        text = decoded.decode('utf-8')
        key = part['mimeType'].lower()
        parts[key] = parts.get(key, '') + ' ' + text
    if 'parts' in big_part:
        for part in big_part['parts']:
            if 'body' in part and 'data' in part['body']:
                decode_and_add(part)
            if 'parts' in part:
                parse_part(part)
    elif big_part.get('body'):
        decode_and_add(big_part)
parse_part(mail['payload'])

if 'text/plain' in parts:
    text = parts['text/plain']
elif 'text/html' in parts:
    text = parts['text/html']
    text = BeautifulSoup(text, 'html.parser').text
else:
    print('NO CONTENT FOR MAIL:')
    print(parts.keys())
    open('debug-mail.json','w').write(json.dumps(mail, indent=2))
    # TODO
    text = ''

print(parts['text/plain'])
# print(parts)
