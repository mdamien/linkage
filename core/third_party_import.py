import io, csv, email, json, re

from email import header
from email.utils import getaddresses
from email.utils import getaddresses

from bs4 import BeautifulSoup

import arxiv
import chardet
from chardet.universaldetector import UniversalDetector
import requests
import xmltodict
from TwitterAPI import TwitterAPI, TwitterRestPager

from raven.contrib.django.raven_compat.models import client

def arxiv_to_csv(q, limit=500):
    results = arxiv.query(q, prune=True, start=0, max_results=limit)

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


def hal_to_csv(q, limit=500):
    params = {
        'fl': 'authFullName_s,title_s',
        'q': q,
        'rows': limit,
    }
    resp = requests.get('https://api.archives-ouvertes.fr/search/', params=params)
    results = resp.json()['response']['docs']

    output = io.StringIO()
    writer = csv.writer(output)

    N = len(results)

    print('HAL search for', q, '; results:', N)
    for result in results:
        authors = result['authFullName_s'][:7] # constrain the authors to avoid exponential edge growth
        for i, author in enumerate(authors):
            for author2 in authors[i+1:]:
                writer.writerow([author, author2, result['title_s'][0]])

    return output.getvalue()

def pubmed_to_csv(q, limit=500):
    output = io.StringIO()
    writer = csv.writer(output)

    BASE = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/'
    url = BASE + 'esearch.fcgi?db=pubmed&retmode=json&retmax=20&sort=relevance&term=fever'

    params = {
        'db': 'pubmed',
        'retmode': 'json',
        'retmax': limit,
        'sort': 'relevance',
        'term': q,
    }
    resp = requests.get(BASE + 'esearch.fcgi', params=params)
    ids = resp.json()['esearchresult']['idlist']
    print('PUBMED search for', q, ':', len(ids), 'papers found')
    if len(ids) == 0:
        return ''

    params = {
        'db': 'pubmed',
        'retmode': 'xml',
        'id': ','.join(ids),
    }
    resp = requests.get(BASE + 'efetch.fcgi', params=params)
    xml = xmltodict.parse(resp.text)

    for pubarticle in xml['PubmedArticleSet']['PubmedArticle']:
        article = pubarticle['MedlineCitation']['Article']
        authors = []
        if 'AuthorList' not in article:
            print('ERROR: NO author list for ', article.get('ArticleTitle'))
            continue
        raw_authors = article['AuthorList']['Author']
        if type(raw_authors) is not list:
            raw_authors = [raw_authors]
        raw_authors = raw_authors[:7] # constrain the authors to avoid exponential edge growth
        for author in raw_authors:
            if 'CollectiveName' in author:
                authors.append(author['CollectiveName'])
            else:
                if 'LastName' or 'ForeName' in authors:
                    authors.append(author.get('LastName', '') + ' ' + author.get('ForeName', ''))
                else:
                    raise Exception('Author with no infos:', author)
        abstract = []
        if 'Abstract' in article:
            abstract = article['Abstract']['AbstractText']
            if type(abstract) is not list:
                abstract = [abstract]
            abstract = [x['#text'] if '#text' in x else x for x in abstract if not (not '#text' in x and '@Label' in x)]
        title = []
        if 'ArticleTitle' in article:
            title = [article['ArticleTitle']]
        text = '\n'.join(title + abstract)
        for i, author in enumerate(authors):
            for author2 in authors[i+1:]:
                writer.writerow([author, author2, text])

    return output.getvalue()


def loklak_to_csv(q, limit=500):
    params = {
        'q': q,
        'maximumRecords': limit,
    }

    output = io.StringIO()
    writer = csv.writer(output)

    len_all = 0
    offset = ''
    while True:
        params['q'] = q + offset
        resp = requests.get('https://api.loklak.org/api/search.json', params=params)
        results = resp.json()['statuses']

        N = len(results)
        len_all += N

        if N == 0:
            break

        print('Twitter search for', q, '; results:', N , ' - offset=', offset)

        for result in results:
            author = result['screen_name']
            mentions = result['mentions']
            text = re.sub(r'https?:\/\/.*[\r\n]*', '', result['text'], flags=re.MULTILINE)
            for mention in mentions:
                writer.writerow([author, mention, text])
            if len(mentions) == 0:
                writer.writerow([author, author, text])

        new_offset = ' until:' + results[-1]['timestamp']
        if new_offset == offset:
            break
        offset = new_offset
        if len_all >= limit:
            break
    
    print('Twitter search for', q, '; results total:', len_all)

    return output.getvalue()



def twitter_to_csv(q, limit=500):
    consumer_key='AufuRL0LOPWf39gEJSXl0Eg6M'
    consumer_secret='n0YDsmnnAjHcgNDFSTTsWny8yAJGeMVq14RNVVkHWMNmsFoYTO'
    access_token_key='131772959-OnVIRfs1l2B2vNZ809DAwSKXZIF6jBFycLr6RNHN'
    access_token_secret='OdBVFgyRW6zcjQKLqgFZrjwCrYymsNEXUNEW8RE2A34f2'
    api = TwitterAPI(consumer_key, consumer_secret, access_token_key, access_token_secret)

    output = io.StringIO()
    writer = csv.writer(output)

    api = TwitterAPI(consumer_key, consumer_secret, access_token_key, access_token_secret)

    count = 0
    r = TwitterRestPager(api, 'search/tweets', {'q': q, 'count': limit})
    for item in r.get_iterator():
        if 'text' in item:
            count += 1
            author = item['user']['screen_name']
            mentions = item['entities']['user_mentions']
            text = re.sub(r'https?:\/\/.*[\r\n]*', '', item['text'], flags=re.MULTILINE)
            for mention in mentions:
                writer.writerow([author, mention['screen_name'], text])
            if len(mentions) == 0:
                writer.writerow([author, author, text])
        elif 'message' in item and item['code'] == 88:
            print('SUSPEND, RATE LIMIT EXCEEDED: %s\n' % item['message'])
            break

    print('Twitter search for', q, '; results:', count)

    return output.getvalue()


def mbox_to_csv(mbox, subject_only):
    output = io.StringIO()
    writer = csv.writer(output)

    mail = None

    def add_mail():
        if mail:
            msg = email.message_from_string(mail)

            subject = ''
            try:
                subject = header.make_header(header.decode_header(msg['Subject']))
            except TypeError:
                client.captureException('Invalid subject: {}'.format(msg['Subject']))
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
