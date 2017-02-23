import os, sys

from bs4 import BeautifulSoup

# TODO: multiple doctors

no_doctor = 0

directory = sys.argv[1]
for file in os.listdir(directory):
    if file == '1_8567669_20160923.xml':
        pass #import pudb;pu.db
    if file.startswith('.') or '.html' in file:
        continue
    f = open(os.path.join(directory, file))
    soup = BeautifulSoup(f, 'html.parser')
    print(file)
    patient = soup.find('patient').text.strip()
    print('patient:', patient)

    report = BeautifulSoup(soup.find('text').text, 'html.parser')
    open(os.path.join(directory, file)+'.html','w').write(str(report))

    doctor = None
    for tr in report.find_all('tr'):
        tds = tr.find_all('td')
        if len(tds) > 2:
            td = tds[-1]
            if td:
                doctor = tr.find_all('td')[-1].text.replace('\n', '').strip()
                if 'N°' in doctor:
                    for p in reversed(tr.find_all('td')[-2].find_all('p')):
                        if p.text.strip():
                            doctor = p.text.replace('\n', '').strip()
                if doctor :
                    break

    if not doctor:
        no_doctor += 1
    print('docteur:', doctor)
    print()

print('patients without doctor', no_doctor)