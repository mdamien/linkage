import io, csv, email

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
                    for dest in msg['To'].split(','):
                        writer.writerow([sender, dest, msg['Subject']])

    for line in mbox:
        if line.startswith('From '):
            add_mail()
            mail = ''
        mail += line
    add_mail()  
    return output.getvalue()