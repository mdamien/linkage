import io, csv

import arxiv

def arxiv_to_csv(q):
    results = arxiv.query(q, prune=True, start=0, max_results=200)

    output = io.StringIO()
    writer = csv.writer(output)

    for result in results:
        for author in result['authors']:
            writer.writerow([result['title'], author])

    return output.getvalue()
