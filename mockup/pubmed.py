import requests
import xmltodict
from pprint import pprint as pp

BASE = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/'

url = BASE + 'esearch.fcgi?db=pubmed&retmode=json&retmax=20&sort=relevance&term=fever'

resp = requests.get(url)

ids = resp.json()['esearchresult']['idlist']

print(ids)

url = BASE + 'efetch.fcgi?db=pubmed&retmode=xml&id=' + ','.join(ids)

resp = requests.get(url)
xml = xmltodict.parse(resp.text)

for pubarticle in xml['PubmedArticleSet']['PubmedArticle']:
    article = pubarticle['MedlineCitation']['Article']
    authors = []
    for author in article['AuthorList']['Author']:
        if 'CollectiveName' in author:
            authors.append(author['CollectiveName'])
        else:
            authors.append(author['LastName'] + ' ' + author['ForeName'])
    abstract = []
    if 'Abstract' in article:
        abstract = article['Abstract']['AbstractText']
        if type(abstract) is not list:
            abstract = [abstract]
        abstract = [x['#text'] if '#text' in x else x for x in abstract]
    title = []
    if 'ArticleTitle' in article:
        title = [article['ArticleTitle']]
    text = '\n'.join(title + abstract)

    print(authors)
    print(text[:100])
    print()
