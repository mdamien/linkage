import csv, tqdm, re, sys, json

writer = csv.writer(open(sys.argv[2] + '_edges.csv','w'))

for line in tqdm.tqdm(open(sys.argv[1])):
    item = json.loads(line)

    text = item['text']

    if not text.startswith('RT '):
        author = item['user']['screen-name'].lower()
        mentions = re.findall(r'@([A-Za-z0-9_]+)', text)

        text = re.sub(r'https?:\/\/.*[\r\n]*', '', text, flags=re.MULTILINE)
        text = re.sub(r'@([A-Za-z0-9_]+)', '', text, flags=re.MULTILINE)
        text = text.strip()
        for mention in mentions:
            writer.writerow([author, mention.lower(), text])