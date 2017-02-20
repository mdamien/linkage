import io, csv, email

from email import header
from email.utils import parseaddr

import arxiv

def arxiv_to_csv(q):
    results = arxiv.query(q, prune=True, start=0, max_results=100)

    output = io.StringIO()
    writer = csv.writer(output)

    N = len(results)

    print('arxiv search for', q, '; results:', N)
    for result in results:
        for author in result['authors']:
            for author2 in result['authors']:
                if author != author2:
                    writer.writerow([author, author2, result['title']])

    return output.getvalue()

def mbox_to_csv(mbox):
    output = io.StringIO()
    writer = csv.writer(output)

    mail = None

    def add_mail():
        if mail:
            msg = email.message_from_string(mail)

            subject = header.make_header(header.decode_header(msg['Subject']))
            body = str(subject)
            if False:
                body += '\n'
                if msg.is_multipart():
                    for payload in msg.get_payload():
                        body += payload.get_payload()
                else:
                    body += msg.get_payload()

            if msg['To'] and msg['From']:
                for sender in msg['From'].split(','):
                    sender = parseaddr(sender)[1]
                    for dest in msg['To'].split(','):
                        dest = parseaddr(dest)[1]
                        writer.writerow([sender, dest, body])

    for line in mbox:
        if line.startswith('From '):
            add_mail()
            mail = ''
        mail += line
    add_mail()  
    return output.getvalue()