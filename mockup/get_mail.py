import requests, base64

# TODO: batch email requests
# TODO: remove quote (do normal mbox processing)

# user = User.objects.get(...)
# social = user.social_auth.get(provider='google-oauth2')
# access_token = social.extra_data['access_token']

access_token = 'ya29.GltIBMOQaF0N0edku5T2CACrWEBel-IbBxa1Vbhk5GOsG1ayDrkPPvzNY52dm9pByerd5GeM4g66e2nMDCuW66LDF_BfWrzcVBO3zbId0UShsU0pHCK2LgT3ARqR'
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
        print()
    if 'nextPageToken' in resp_json:
        print(resp_json['nextPageToken'])
        params['pageToken'] = resp_json['nextPageToken']
        print(' -#- next page -#-')
    else:
        print(' -#- end pagination -#-')
        break
