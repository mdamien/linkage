import io, csv, email
from email.utils import parseaddr

import arxiv

def arxiv_to_csv(q):
    results = arxiv.query(q, prune=True, start=0, max_results=40)

    output = io.StringIO()
    writer = csv.writer(output)

    N = len(results)

    print('arxiv search for', q, '; results:', N)
    for result in results:
        for author in result['authors']:
            writer.writerow([result['title'], author])

    return output.getvalue()

def mbox_to_csv(mbox):
    output = io.StringIO()
    writer = csv.writer(output)

    mail = None

    def add_mail():
        if mail:
            msg = email.message_from_string(mail)
            if msg['To'] and msg['From']:
                for sender in msg['From'].split(','):
                    sender = parseaddr(sender)[1]
                    for dest in msg['To'].split(','):
                        dest = parseaddr(dest)[1]
                        writer.writerow([sender, dest, msg['Subject']])

    for line in mbox:
        if line.startswith('From '):
            add_mail()
            mail = ''
        mail += line
    add_mail()  
    return output.getvalue()