import pickle



name2taxid = pickle.load( open( "name2taxid.p", "rb" ) )
taxid2name = pickle.load( open( "taxid2name.p", "rb" ) )
taxid2rank = pickle.load( open( "taxid2rank.p", "rb" ) )
taxid2parent = pickle.load( open( "taxid2parent.p", "rb" ) )
parent2child = pickle.load( open( "parent2child.p", "rb" ) )

def get_children(taxon):
	# print('taxon is ~~' + taxon + '~~')
	taxon_taxid = name2taxid.get(taxon, 'none')
	# print(' taxon taxid is ' + str(taxon_taxid))
	children = parent2child.get(taxon_taxid, [])
	return [taxid2name[x] for x in children]

def get_parent(taxon):
	taxon_taxid = name2taxid.get(taxon, 'none')
	taxon_parent_taxid = taxid2parent.get(taxon_taxid, 'none')
	return taxid2name.get(taxon_parent_taxid, 'none')

def get_siblings(taxon):
	return get_children(get_parent(taxon))
print(name2taxid.get('Nematoda'))