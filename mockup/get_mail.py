import requests, base64, csv
from email.utils import getaddresses

# TODO: batch email requests

access_token = 'ya29.GltIBLbYoOPgOKo-wVFUQZpwkge_2er2BDqt_5a9geenerZ4hrLjtlZ0BLjRVTtAOrAMsZzrqZr65lNWcbVyeQHY9TW2iNFuL-ASsi5PaY585kyMuUHFIGgG-uDr'
params = {'access_token': access_token} #, 'maxResults': 2}

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
        else:
            pass
            # TODO

        if 'text/plain' in parts:
            text = parts['text/plain']
        else:
            # TODO
            text = ''

        text = '\n'.join([line for line in text.split('\n') if not line.startswith('>')])

        print(mail_pack['id'])
        print(subject)
        print(text)
        sender = getaddresses([header.get('from')])[0][1]
        for _, dest in getaddresses([header.get('to')] + [header.get('cc','')]):
            if dest:
                print(sender, '->', dest)
        print()
    if 'nextPageToken' in resp_json:
        print(resp_json['nextPageToken'])
        params['pageToken'] = resp_json['nextPageToken']
        print(' -#- next page -#-')
    else:
        print(' -#- end pagination -#-')
        break
