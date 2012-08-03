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

def get_children_multiple(taxon, count):
	current_list = [taxon]
	while count > 0:
		new_list = []
		for current_taxon in current_list:
			new_list.extend(get_children(current_taxon))
		current_list = new_list
		count += -1
	return new_list


def get_parent(taxon):
	taxon_taxid = name2taxid.get(taxon, 'none')
	taxon_parent_taxid = taxid2parent.get(taxon_taxid, 'none')
	return taxid2name.get(taxon_parent_taxid, 'none')

def get_siblings(taxon):
	return filter( lambda x : x != taxon, get_children(get_parent(taxon)))

# print(get_children_multiple('Arthropoda', 1))
# print(get_children_multiple('Arthropoda', 2))