import io, csv, email, json

from email import header
from email.utils import getaddresses
from email.utils import getaddresses

from bs4 import BeautifulSoup

import arxiv
import chardet
from chardet.universaldetector import UniversalDetector
import requests


def arxiv_to_csv(q):
    results = arxiv.query(q, prune=True, start=0, max_results=1000)

    output = io.StringIO()
    writer = csv.writer(output)

    N = len(results)

    print('arxiv search for', q, '; results:', N)
    for result in results:
        authors = result['authors'][:7]
        for i, author in enumerate(authors):
            for author2 in authors[i+1:]:
                writer.writerow([author, author2, result['title']])

    return output.getvalue()


def hal_to_csv(q):
    params = {
        'fl': 'authFullName_s,title_s',
        'q': q,
        'rows': 1000,
    }
    resp = requests.get('https://api.archives-ouvertes.fr/search/', params=params)
    results = resp.json()['response']['docs']

    output = io.StringIO()
    writer = csv.writer(output)

    N = len(results)

    print('HAL search for', q, '; results:', N)
    for result in results:
        authors = result['authFullName_s'][:7]
        for i, author in enumerate(authors):
            for author2 in authors[i+1:]:
                writer.writerow([author, author2, result['title_s'][0]])

    return output.getvalue()


def mbox_to_csv(mbox, subject_only):
    output = io.StringIO()
    writer = csv.writer(output)

    mail = None

    def add_mail():
        if mail:
            msg = email.message_from_string(mail)

            subject = header.make_header(header.decode_header(msg['Subject']))
            body = str(subject)
            if not subject_only:
                body += '\n'

                text_body = ''
                html_body = ''

                def parse_payload(message):
                    if message.is_multipart():
                        for part in message.get_payload(): 
                            yield from parse_payload(part)
                    else:
                        cte = message.get_content_type()
                        if 'plain' in cte or 'html' in cte:
                            yield message, message.get_payload(decode=True)

                for submsg, part in parse_payload(msg):
                    content_type = submsg.get_content_type()
                    content = ''
                    def decode():
                        charset = submsg.get_content_charset('utf-8')
                        try:
                            return part.decode(charset)
                        except UnicodeDecodeError:
                            detector = UniversalDetector()
                            detector.feed(part)
                            detector.close()
                            try:
                                return part.decode(detector.result['encoding'])
                            except UnicodeDecodeError as e:
                                for prober in detector._charset_probers:
                                    if prober.get_confidence() > detector.MINIMUM_THRESHOLD:
                                        try:
                                            return part.decode(prober.charset_name)
                                        except UnicodeDecodeError:
                                            pass
                                raise e
                    if 'plain' in content_type:
                        content = decode()
                        lines = [line for line in content.split('\n') if not line.startswith('>')]
                        text_body += '\n' + '\n'.join(lines)
                    if 'html' in content_type:
                        content = BeautifulSoup(decode()).text
                        html_body += '\n' + content

                if text_body:
                    body += text_body
                else:
                    body += html_body

            if msg['To'] and msg['From']:
                for _, sender in getaddresses(msg.get_all('from', [])):
                    tos = msg.get_all('to', [])
                    ccs = msg.get_all('cc', [])
                    resent_tos = msg.get_all('resent-to', [])
                    resent_ccs = msg.get_all('resent-cc', [])
                    all_recipients = getaddresses(tos + ccs + resent_tos + resent_ccs)
                    for _, dest in all_recipients:
                        writer.writerow([sender, dest, body])

    for line in mbox:
        if line.startswith('From '):
            add_mail()
            mail = ''
        if mail is not None: # ignore email without headers
            mail += line
    add_mail()  
    return output.getvalue()
