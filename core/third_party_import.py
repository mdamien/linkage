import io, csv, email

from email import header
from email.utils import parseaddr, getaddresses
from email.utils import getaddresses

from django.utils.html import strip_tags

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

def mbox_to_csv(mbox, subject_only):
    output = io.StringIO()
    writer = csv.writer(output)

    mail = None

    def add_mail():
        if mail:
            msg = email.message_from_string(mail)

            try:
                subject = header.make_header(header.decode_header(msg['Subject']))
            except:
                subject = msg['Subject']
            body = str(subject)
            if not subject_only:
                body += '\n'
                if msg.is_multipart():
                    # todo: RLYY ? make it recursive
                    for payload in msg.get_payload():
                        subpayloads = payload.get_payload()
                        if type(subpayloads) is list:
                            for subpayload in subpayloads:
                                subsubpayloads = subpayload.get_payload()
                                if type(subsubpayloads) is list:
                                    for subsubpayload in subsubpayloads:
                                        body += '\n' + strip_tags(subsubpayload.get_payload())
                                else:
                                    body += '\n' + strip_tags(subsubpayloads)
                        else:
                            body += '\n' + strip_tags(subpayloads)
                else:
                    body += '\n' + strip_tags(msg.get_payload())

            if msg['To'] and msg['From']:
                for _, sender in getaddresses(msg.get_all('from', [])):
                    tos = msg.get_all('to', [])
                    ccs = msg.get_all('cc', [])
                    resent_tos = msg.get_all('resent-to', [])
                    resent_ccs = msg.get_all('resent-cc', [])
                    all_recipients = getaddresses(tos + ccs + resent_tos + resent_ccs)
                    for _, dest in all_recipients:
                        writer.writerow([sender, dest, body])

    for line in mbox:
        if line.startswith('From '):
            add_mail()
            mail = ''
        mail += line
    add_mail()  
    return output.getvalue()