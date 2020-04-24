import requests
from urllib.parse import quote_plus, urljoin
from bs4 import BeautifulSoup
from minet import multithreaded_fetch


def extract_paper_data(url, html):
    soup = BeautifulSoup(html, 'lxml')
    data = {}

    data['title'] = soup.select_one('#page-title').text
    data['abstract'] = soup.select_one('#abstract-1').text
    data['url'] = url

    data['authors'] = []
    for author in soup.select('.highwire-citation-author'):
        data['authors'].append(author.text)

    return data


def extract_links(soup):
    links = soup.select('.pane-highwire-search-results .highwire-cite-linked-title')

    for link in links:
        yield urljoin("https://www.medrxiv.org/", link.attrs['href'])


def search(q, verbose=False, limit=None):
    results_per_page = 50
    base_url = "https://www.medrxiv.org/search/{} numresults%3A{}%20sort%3Arelevance-rank?page="
    base_url = base_url.format(q, results_per_page)

    if verbose: print('fetch first page')
    resp = requests.get(base_url)
    soup = BeautifulSoup(resp.text, 'lxml')
    links = list(extract_links(soup))

    if len(links) == results_per_page and (limit is None or len(links) < limit):
        if verbose: print('fetching remaining pages')
        last_page = int(soup.select_one('.pager-last').text)

        if limit is not None:
            last_page = limit // results_per_page
            if limit % results_per_page != 0:
                last_page += 1

        pages_url = [base_url+str(page) for page in range(1, last_page)]
        for result in multithreaded_fetch(pages_url, domain_parallelism=20):
            if result.error is not None:
                raise Exception(result.error)
            else:
                if verbose: print('page:', result.url)
                html = result.response.data.decode('utf-8')
                soup = BeautifulSoup(html, 'lxml')
                links += extract_links(soup)
                if verbose: print('links:', len(links))

    if limit is not None:
        links = links[:limit]

    # parallel fetch of all the papers
    if verbose: print('fetching papers')
    papers = []

    for result in multithreaded_fetch(links, domain_parallelism=20):
        if result.error is not None:
            raise Exception(result.error)
        else:
            html = result.response.data.decode('utf-8')
            papers.append(extract_paper_data(result.url, html))
            if verbose: print(len(papers), '/', len(links))

    return papers


if __name__ == '__main__':
    for paper in search('covid', verbose=True):
        print(paper)