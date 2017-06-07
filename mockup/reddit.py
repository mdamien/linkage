import requests, csv

# optional: makes requests-cache make it easy to cache your results
# import requests_cache
# requests_cache.install_cache('reddit_cache')

# where we store all the rows
DATA = []

def get(url, args={}):
    print('GET', url, args)
    try:
        resp = requests.get(url, args, headers={'User-agent': 'linkage.fr'})
        return resp.json()
    except Exception as e:
        print(resp.text)
        raise e

def parse_comment(comment, reply_to=None):
    if 'body' in comment:
        replies = comment.get('replies', [])
        replies = comment.get('children') if replies else []
        author = comment.get('author', 'no-author')
        if replies:
            replies = [parse_comment(reply['data'], author) for reply in replies]
        if author != '[deleted]' and reply_to != '[deleted]':
            DATA.append([author, reply_to, comment.get('body',None)])

def parse_post(post):
    content = get('https://www.reddit.com' + post['permalink'] + '.json')
    comments = content[1]['data']['children']
    comments = [parse_comment(comment['data'], post['author']) for comment in comments]
    self_post = content[0]['data']['children'][0]['data'].get('body')

count = 0
last_post_id = ''
while True:
    resp = get('https://www.reddit.com/r/django/top/.json', {
        'count': count,
        'after': last_post_id,
        'sort': 'top',
        't': 'all'
    })
    posts = resp['data']['children']
    for post in posts:
        post = post['data']
        print(post['title'])
        parse_post(post)
        count += 1
    last_post_id = resp['data']['after']
    print('COUNT:', count, last_post_id)
    print(len(DATA))
    if count > 100:
        break

writer = csv.writer(open('reddit.csv', 'w'))
for row in DATA:
    writer.writerow(row)
