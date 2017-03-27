import xmltodict, csv, tqdm

nodes = []
node = None
edge = None

nodes_csv = csv.writer(open('nodes.csv','w'))
edges_csv = csv.writer(open('edges.csv','w'))

nodes_csv.writerow(['id','label'])
edges_csv.writerow(['source','target', 'weight', 'type', 'emotion', 'text'])

def write_stuff():
    if node:
        nodes_csv.writerow([node['@id'], node[11]['value'].strip()])
    if edge:
        if type(edge[0]) is list:
            # remove mention from retweets
            retweet_dates = set()
            for cat in edge[0]:
                if cat['value'] == 'retweet':
                    retweet_dates.add(cat['start'])

            for i, cat in enumerate(edge[0]):
                if cat['value'] == 'mention' and cat['start'] in retweet_dates:
                    continue
                if cat['value'] == 'co-mention':
                    continue

                edges_csv.writerow([edge['@source'], edge['@target'], edge['@weight'],
                    edge[0][i]['value'], edge[1][i]['value'], edge[2][i]['value'].strip()])
        else:
            edges_csv.writerow([edge['@source'], edge['@target'], edge['@weight'],
                edge[0]['value'], edge[1]['value'], edge[2]['value']])

for line in tqdm.tqdm(open('presidentielles_big.gexf')):
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