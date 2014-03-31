import pickle

names = open("names.dmp")

name2taxid = {}
taxid2name = {}

processed = 0
for line in names:
    processed = processed + 1
    if processed %10000 == 0:
        print(processed)
    taxid, name, other_name, type = line.rstrip('\t|\n').split("\t|\t")
    name2taxid[name] = int(taxid)
    if type == 'scientific name':
        taxid2name[int(taxid)] = name


taxid2rank = {}
taxid2parent = {}

#store parent to child relationships
parent2child = {}

processed = 0
nodes = open("nodes.dmp")
for line in nodes:
    processed = processed + 1
#    if processed %10000 == 0:
#        print(processed)
    taxid, parent, rank = line.rstrip('\t|\n').split("\t|\t")[0:3]
    taxid = int(taxid)
    parent = int(parent)
    taxid2rank[int(taxid)] = rank
    taxid2parent[int(taxid)] = int(parent)
    if parent not in parent2child:
        parent2child[parent] = []
    parent2child[parent].append(taxid)


pickle.dump( name2taxid, open( "name2taxid.p", "wb" ) )
pickle.dump( taxid2name, open( "taxid2name.p", "wb" ) )
pickle.dump( taxid2rank, open( "taxid2rank.p", "wb" ) )
pickle.dump( taxid2parent, open( "taxid2parent.p", "wb" ) )
pickle.dump( parent2child, open( "parent2child.p", "wb" ) )