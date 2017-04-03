import xmltodict, csv, tqdm, re, sys

node = None
edge = None

nodes_csv = csv.writer(open(sys.argv[2] + '_nodes.csv','w'))
edges_csv = csv.writer(open(sys.argv[2] + '_edges.csv','w'))

nodes_csv.writerow(['id','label'])
edges_csv.writerow(['source','target', 'weight', 'type', 'emotion', 'text'])

# todo: garder que les comment et les mentions [ok]
# todo: regarder un comm genere une mention de la personne dans le tweet commenté

def write_stuff():
    if node:
        nodes_csv.writerow([node['@id'], node[11]['value'].strip()])
    if edge:
        def clean_text(text):
            return text.strip()

        if type(edge[0]) is list:
            for i, cat in enumerate(edge[0]):
                text = clean_text(edge[2][i]['value'])
                if text.startswith('RT '):
                    continue
                elif cat['value'] == 'co-mention':
                    continue
                elif cat['value'] == 'retweet':
                    continue
                else:
                    edges_csv.writerow([edge['@source'], edge['@target'], edge['@weight'],
                        cat['value'], edge[1][i]['value'], text])
        else:
            text = clean_text(edge[2]['value'])
            if text.startswith('RT '):
                return
            cat = edge[0]['value']
            if cat == 'co-mention':
                return
            edges_csv.writerow([edge['@source'], edge['@target'], edge['@weight'],
                cat, edge[1]['value'], text])


for line in tqdm.tqdm(open(sys.argv[1])):
    if '<node id=' in line:
        write_stuff()
        node = xmltodict.parse(line + '</node>')['node']
        edge = None
    if '<edge id=' in line:
        if edge is None:
            print()
            print('nodes OK, doing edges')
        write_stuff()
        edge = xmltodict.parse(line + '</edge>')['edge']
        node = None
    if node is not None or edge is not None:
        v = node if node is not None else edge
        if '<attvalue ' in line:
            att = xmltodict.parse(line)['attvalue']
            key = int(att['@for'])
            att_val = {
                'value': att['@value'],
            }
            if '@start' in att:
                att_val['start'] = att.get('@start')
            if key in v:
                if type(v[key]) is not list:
                    v[key] = [v[key]]
                v[key].append(att_val)
            else:
                v[key] = att_val
