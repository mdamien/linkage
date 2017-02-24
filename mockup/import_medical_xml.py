import os, sys, csv

from bs4 import BeautifulSoup

with_doctor = 0
no_doctor = 0

directory = sys.argv[1]
dest = sys.argv[2]
writer = csv.writer(open(dest, 'w'))

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
    # open(os.path.join(directory, file)+'.html','w').write(str(report))

    doctors = []
    for tr in report.find_all('tr'):
        tds = tr.find_all('td')
        if len(tds) > 2:
            td = tds[-1]
            if td:
                doctor = tr.find_all('td')[-1].text.replace('\n', '').strip()
                if 'N°' in doctor:
                    for p in reversed(tr.find_all('td')[-2].find_all('p')):
                        if p.text.strip(): # :(
                            doctor = p.text.replace('\n', '').strip()
                else:
                    for p in tr.find_all('td')[-1].find_all('p'):
                        name = p.text.strip()
                        if 'Date de r' in doctor:
                            break
                        if name:
                            doctors.append(name)
                if 'EXAMEN' in doctor:
                    doctor = ''
                if 'Date de r' in doctor:
                    break
                if not doctors and doctor:
                    doctors = [doctor]
                if doctors:
                    break

    print('docteurs:', doctors)
    print()

    if not doctors:
        no_doctor += 1
    else:
        with_doctor += 1
        for doctor in doctors:
            writer.writerow([patient, doctor, report.text])

print('patients without doctor', no_doctor)
print('patients with doctor (imported)', with_doctor)