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

from raven.contrib.django.raven_compat.models import client

from django.conf import settings


from .medrxiv_search import search as medrxiv_search


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
                writer.writerow([author, author2, result['title'] + '\n' + result.get('summary', '')])

    return output.getvalue()


def biorxiv_to_csv(q, limit=500):
    params = {
        'q': q,
        'page_size': 250,
        'page': 0,
    }

    results = []

    while True:
        resp = requests.get('https://api.rxivist.org/v1/papers', params=params).json()
        results += resp['results']
        if resp['query']['current_page'] == resp['query']['final_page']:
            break
        else:
            params['page'] += 1

    output = io.StringIO()
    writer = csv.writer(output)

    N = len(results)

    print('biorxiv search for', q, '; results:', N)
    for result in results:
        authors = result['authors'][:7]
        for i, author in enumerate(authors):
            for author2 in authors[i+1:]:
                writer.writerow([author['name'], author2['name'], result['title'] + '\n' + result.get('abstract', '')])

    return output.getvalue()


def medrxiv_to_csv(q, limit=500):
    results = medrxiv_search(q, verbose=True, limit=limit)

    output = io.StringIO()
    writer = csv.writer(output)

    N = len(results)

    print('medrxiv search for', q, '; results:', N)
    for result in results:
        authors = result['authors'][:7]
        for i, author in enumerate(authors):
            for author2 in authors[i+1:]:
                writer.writerow([author, author2, result['title'] + '\n' + result['abstract']])

    return output.getvalue()


def hal_to_csv(q, limit=500):
    params = {
        'fl': 'authFullName_s,title_s,abstract_s',
        'q': q,
        'rows': limit,
    }

    results = []
    while True:
        resp = requests.get('https://api.archives-ouvertes.fr/search/', params=params)
        results += resp.json()['response']['docs']
        if len(results) >= resp.json()['response']['numFound'] or len(results) > limit:
            break
        params['start'] = len(results)

    output = io.StringIO()
    writer = csv.writer(output)

    N = len(results)

    print('HAL search for', q, '; results:', N)
    for result in results:
        if 'authFullName_s' in result:
            authors = result['authFullName_s'][:7] # constrain the authors to avoid exponential edge growth
            for i, author in enumerate(authors):
                for author2 in authors[i+1:]:
                    writer.writerow([author, author2, result['title_s'][0] + '\n' + result.get('abstract_s', [''])[0]])

    return output.getvalue()


def pubmed_keywords_to_csv(q, limit=500):
    return pubmed_to_csv(q, limit=limit, use_keywords=True)


def pubmed_to_csv(q, limit=500, use_keywords=False):
    output = io.StringIO()
    writer = csv.writer(output)

    for paper in _pubmed_search(q, limit=limit):
        for i, author in enumerate(paper['authors']):
            for author2 in paper['authors'][i+1:]:
                writer.writerow([author, author2, paper['keywords'] if use_keywords else paper['text']])

    return output.getvalue()



def _pubmed_search(q, limit=500):
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

    yield from _pubmed_content(ids)


def _chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i + n]


def _pubmed_content(ids):
    for chunk in _chunks(ids, 100):
        params = {
            'db': 'pubmed',
            'retmode': 'xml',
            'id': ','.join(chunk),
        }
        resp = requests.get('https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi', params=params)
        xml = xmltodict.parse(resp.text)
        open('pubmed.json', 'w').write(json.dumps(xml, indent=2))

        articles = xml['PubmedArticleSet']['PubmedArticle']
        if type(articles) is not list:
            articles = [articles]
        for pubarticle in articles:
            article = pubarticle['MedlineCitation']['Article']
            authors = []
            if 'AuthorList' not in article:
                print('ERROR: NO author list for ', article.get('ArticleTitle'))
                print(article)
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
                if not abstract:
                    abstract = []
                if type(abstract) is not list:
                    abstract = [abstract]
                abstract = [x['#text'] if '#text' in x else x for x in abstract if not (not '#text' in x and '@Label' in x)]
            title = []
            if 'ArticleTitle' in article:
                title = [article['ArticleTitle']]

            keywords = []
            xml_keywords = pubarticle['MedlineCitation'].get('KeywordList', {}).get('Keyword', [])
            if type(xml_keywords) is not list:
                xml_keywords = [xml_keywords]
            for keyword in xml_keywords:
                try:
                    keywords.append(keyword['#text'].replace(' ', '_'))
                except:
                    print('problem importing keyword', xml_keywords, keyword)
            keywords = ' '.join(keywords)

            from collections import OrderedDict
            if title and type(title[0]) is OrderedDict: title = [title[0]['#text']]
            if abstract and type(abstract[0]) is OrderedDict:
              print('Invalid abstract for', article)
              abstract = ['']

            title = [x for x in title if x]
            abstract = [x for x in abstract if x]

            text = ''
            try:
              text = '\n'.join(title + abstract)
            except TypeError:
              print('Invalid title or abstract', title, '/', abstract)

            authors = list(set(authors[:2]).union(set(authors[-2:])))

            yield {
                'id': pubarticle['MedlineCitation']['PMID']['#text'],
                'text': text,
                'keywords': keywords,
                'authors': authors,
            }


def pubmed_citations_to_csv(q, limit=500):
    """
    1- Récupérer tous les articles sur PubMed sur un sujet (comme avant)
    2- Réupérer (toujours sur PubMed) les citations UNIQUEMENT entre ces articles

    Pour la construction du graphe : 

    lien entre chercheur A et chercheur B : si le chercheur A a écrit un article C qui cite le chercheur B. Texte associé : abstract de l'article C
    """
    # get pubmed articles
    articles = list(_pubmed_search(q, limit=limit))
    articles_by_ids = {article['id']: article for article in articles}

    # get pubmed citations
    cited_by = {}
    articles_ids = list(articles_by_ids.keys())
    for chunk in _chunks(articles_ids, 100):
        params = {
            'dbfrom': 'pubmed',
            'linkname': 'pubmed_pubmed_citedin',
            'id': chunk,
            'retmode': 'json',
        }
        resp = requests.get('https://eutils.ncbi.nlm.nih.gov/entrez/eutils/elink.fcgi', params=params)
        for linkset in resp.json()['linksets']:
            article_id = linkset['ids'][0]
            if 'linksetdbs' in linkset:
                linkset_ids = linkset['linksetdbs'][0]['links']
                linkset_ids = [id for id in linkset_ids if id in articles_by_ids]
                cited_by[article_id] = linkset_ids
                print(article_id, 'cited_by', len(cited_by[article_id]))
            else:
                cited_by[article_id] = []

    output = io.StringIO()
    writer = csv.writer(output)

    for article in articles:
        for other_article_id in cited_by[article['id']]:
            other_article = articles_by_ids[other_article_id]
            for author in article['authors'][:7]:
                for author2 in other_article['authors'][:7]:
                    writer.writerow([author, author2, other_article['text']])

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

        print('Twitter/loklak search for', q, '; results:', N , ' - offset=', offset)

        for result in results:
            author = result['screen_name'].lower()
            mentions = result['mentions']
            text = re.sub(r'https?:\/\/.*[\r\n]*', '', result['text'], flags=re.MULTILINE)
            text = re.sub(r'@([A-Za-z0-9_]+)', '', text, flags=re.MULTILINE)
            for mention in mentions:
                writer.writerow([author, mention.lower(), text])
            if len(mentions) == 0:
                writer.writerow([author, author, text])

        new_offset = ' until:' + results[-1]['timestamp']
        if new_offset == offset:
            break
        offset = new_offset
        if len_all >= limit:
            break
    
    print('Twitter/loklak search for', q, '; results total:', len_all)

    return output.getvalue()



def twitter_to_csv(q, limit=500):
    consumer_key = settings.TWITTER_CONSUMER_KEY
    consumer_secret = settings.TWITTER_CONSUMER_SECRET
    access_token_key = settings.TWITTER_ACCESS_TOKEN_KEY
    access_token_secret = settings.TWITTER_ACCESS_TOKEN_SECRET
    api = TwitterAPI(consumer_key, consumer_secret, access_token_key, access_token_secret)

    output = io.StringIO()
    writer = csv.writer(output)

    api = TwitterAPI(consumer_key, consumer_secret, access_token_key, access_token_secret)

    count = 0
    r = TwitterRestPager(api, 'search/tweets', {'q': q, 'count': 100})
    for item in r.get_iterator():
        if 'text' in item:
            count += 1
            author = item['user']['screen_name'].lower()
            mentions = item['entities']['user_mentions']
            text = re.sub(r'https?:\/\/.*[\r\n]*', '', item['text'], flags=re.MULTILINE)
            text = re.sub(r'@([A-Za-z0-9_]+)', '', text, flags=re.MULTILINE)
            for mention in mentions:
                writer.writerow([author, mention['screen_name'].lower(), text])
            if len(mentions) == 0:
                writer.writerow([author, author, text])
        elif 'message' in item and item['code'] == 88:
            print('SUSPEND, RATE LIMIT EXCEEDED: %s\n' % item['message'])
            break
        if count > limit:
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
                        content = BeautifulSoup(decode(), 'html.parser').text
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

def gmail_to_csv(access_token, limit):
    output = io.StringIO()
    writer = csv.writer(output)

    params = {'access_token': access_token}

    c = 0
    while True:
        response = requests.get(
            'https://www.googleapis.com/gmail/v1/users/me/messages/',
            params=params
        )
        resp_json = response.json()
        if 'messages' not in resp_json:
            print(resp_json)
        mails = resp_json['messages']
        print(len(mails), 'mails')
        for mail_pack in mails:
            response = requests.get(
                'https://www.googleapis.com/gmail/v1/users/me/messages/' + mail_pack['id'],
                params={'access_token': access_token}
            )
            mail = response.json()
            if 'CHAT' in mail['labelIds']: # ignore hangout messages
                continue
            subject = None
            try:
                header = {}
                for item in mail['payload']['headers']:
                    header[item['name'].lower()] = item['value']
                subject = header['subject']
            except:
                pass

            parts = {}
            if 'parts' in mail['payload']:
                for part in mail['payload']['parts']:
                    if 'body' in part and 'data' in part['body']:
                        data = part['body']['data']
                        decoded = base64.b64decode(data.replace('-','+').replace('_','/'))
                        text = decoded.decode('utf-8')
                        parts[part['mimeType'].lower()] = text
            elif mail.get('payload', {}).get('body'):
                part = mail['payload']
                data = part['body']['data']
                decoded = base64.b64decode(data.replace('-','+').replace('_','/'))
                text = decoded.decode('utf-8')
                parts[part['mimeType'].lower()] = text
            else:
                pass
                # TODO ATTENTION - PLAIN TEXT CAN BE EMPTY
                # TODO: MULTIPLE PARTS ???

            if 'text/plain' in parts:
                text = parts['text/plain']
            elif 'text/html' in parts:
                text = parts['text/html']
                text = BeautifulSoup(text, 'html.parser').text
            else:
                print('NO CONTENT FOR MAIL:')
                print(parts)
                # open('debug-mail.json', 'w').write(json.dumps(mail, indent=2))
                # TODO
                text = ''

            # QUOTE REMOVING DISABLED (keep old messages)
            # text = '\n'.join([line for line in text.split('\n') if not line.startswith('>')])

            # print(mail_pack['id'])
            # print(subject)
            # print(text)
            
            text = text if text else ''
            subject = subject if subject else ''

            sender = getaddresses([header.get('from', '')])[0][1]
            for _, dest in getaddresses([header.get('to', '')] + [header.get('cc', '')]):
                if dest:
                    # print(sender, '->', dest)
                    writer.writerow([sender, dest, subject + '\n' + text])
            c += 1
            # print('mail-',c)
            if c > limit:
                break
            # print()
        if c > limit:
            break
        if 'nextPageToken' in resp_json:
            print(resp_json['nextPageToken'])
            params['pageToken'] = resp_json['nextPageToken']
            print(' -#- next page -#-')
        else:
            print(' -#- end pagination -#-')
            break

    return output.getvalue()
