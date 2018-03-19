import csv
import sys
import re

def normalize(str):
    return re.sub(' +',' ',str.replace("-", " ").replace("(", "").replace(")", "").replace(",", "").replace("/", " "))

def truecase(truecased_names, uppercased_name):
    true_map = {}
    truecased_name = ""
    for syn in truecased_names:
        for w in syn.split(" "):
            true_map[w.lower()] = w
    for w in uppercased_name.split(" "):
        try:
            truecased_name += true_map[w.lower()]
        except KeyError:
            truecased_name += w
        truecased_name += " "
    return truecased_name.strip()

max_len = 32
entities_dict = {}
with open(sys.argv[1]) as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        if (row['uniprotAcc'] != ''):
            try:
                entities_dict[row['uniprotAcc']].add(normalize(row['uniprotRecommendedName']))
            except KeyError:
                entities_dict[row['uniprotAcc']] = {normalize(row['uniprotRecommendedName'])}
            if (row['uniprotAlternativeNames'] != ''):
                entities_dict[row['uniprotAcc']].update(normalize(row['uniprotAlternativeNames']).split("#"))
            if (row['authorAssignedEntityName'] != ''):
                entities_dict[row['uniprotAcc']].add(truecase(entities_dict[row['uniprotAcc']], normalize(row['authorAssignedEntityName'])))
#            if (row['synonym'] != ''):
#                entities_dict[row['uniprotAcc']].update(normalize(row['synonym']).split("#"))

n = 0
m = 0
e = 0
with open(sys.argv[2], 'wb') as csvfile:
    writer = csv.writer(csvfile)
    for key in entities_dict:
       n = n + len(entities_dict[key])
       short_syns = []
       for syn in entities_dict[key]:
           if (len(syn) > 0) & (len(syn) <= max_len):
               short_syns.append(syn)
       if len(short_syns) > 0:
           e = e + 1
           m = m + len(short_syns)
           writer.writerow(["protein", key]+short_syns)

print "keys:", len(entities_dict), e
print "syns:", n, m
