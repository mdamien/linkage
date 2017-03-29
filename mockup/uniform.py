import sys, csv

out = csv.writer(open('out.csv', 'w'))
for line in csv.reader(open(sys.argv[1])):
    if len(line) == 3:
        a, b, text = line
        text = 'aaa aa  aa bbbb jjjj retttt asda adsdsa dasdsadsa'
        out.writerow([a,b,text])
