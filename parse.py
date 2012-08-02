from modgrammar import *
import tax

class TaxonName (Grammar):
	grammar = (WORD("A-Za-z "))

class TaxonExtension (Grammar):
	grammar = (L("children") | L("parent") | L("siblings"))

class TaxonFull (Grammar):
	grammar = ( TaxonName, OPTIONAL(':', TaxonExtension) )
	grammar_tags = ("list element",)


class TaxonList (Grammar):
	grammar = (  '(' , LIST_OF(OR(TaxonFull, REF('TaxonList')), sep=",") , ')'  )
	grammar_tags = ("list element",)

class Tree (Grammar):
	grammar = (  TaxonList  )


tree_parser = Tree.parser()



def expand_taxon(taxon):
	# print(repr(taxon))
	taxon_name = taxon.elements[0].string
	taxon_extension = taxon.elements[1]
	# if the extension is none, then just add the name 
	if taxon_extension == None:
		return [taxon_name]
	else:
		# print(taxon_extension)
		# deal with children
		if taxon_extension.string == ':children':
			return tax.get_children(taxon_name)
		if taxon_extension.string == ':parent':
			return [tax.get_parent(taxon_name)]
		if taxon_extension.string == ':siblings':
			return tax.get_siblings(taxon_name)


def list_subtrees(tree, level = 0):
	if tree == None:
		return
	for subtree in tree.find_tag_all("list element"):
		print('   ' * level + repr(subtree))
		list_subtrees(subtree, level+1)


def parse_rec(tree, level = 0):
	result = []
	for subtree in tree.find_tag_all("list element"):
		if isinstance(subtree, TaxonFull):
			result.extend(expand_taxon(subtree))
		if isinstance(subtree, TaxonList):
			result.append(parse_rec(subtree))
	return result




# some tests to make sure we don't break anything

# test flat lists of simple names
assert (parse_rec(tree_parser.parse_string('(nematoda)').find(TaxonList))) == ['nematoda']
assert (parse_rec(tree_parser.parse_string('(nematoda, arthropoda, sea spiders)').find(TaxonList))) == ['nematoda', 'arthropoda', 'sea spiders']

# test children, sibling, parent extensions
assert (parse_rec(tree_parser.parse_string('(Nematoda:children, arthropoda, sea spiders)').find(TaxonList))) == ['unclassified Nematoda', 'Enoplea', 'Chromadorea', 'Nematoda environmental samples', 'arthropoda', 'sea spiders']
assert (parse_rec(tree_parser.parse_string('(Coleoptera:parent, Nematoda, Eutheria)').find(TaxonList))) == ['Endopterygota', 'Nematoda', 'Eutheria']
assert (parse_rec(tree_parser.parse_string('(Coleoptera:siblings)').find(TaxonList))) == ['Diptera', 'Hymenoptera', 'Siphonaptera', 'Mecoptera', 'Strepsiptera', 'Amphiesmenoptera', 'Neuropterida']

# test structured trees with simple names
assert (parse_rec(tree_parser.parse_string('(Nematoda, (Tardigrada, Coleoptera))').find(TaxonList))) == ['Nematoda', ['Tardigrada', 'Coleoptera']]
assert (parse_rec(tree_parser.parse_string('(Nematoda, (Tardigrada, (Homo, Pan), Coleoptera))').find(TaxonList))) == ['Nematoda', ['Tardigrada', ['Homo', 'Pan'], 'Coleoptera']]

# test structured trees with extensions
assert (parse_rec(tree_parser.parse_string('(Nematoda:children, (Coleopter, Diptera))').find(TaxonList))) == ['unclassified Nematoda', 'Enoplea', 'Chromadorea', 'Nematoda environmental samples', ['Coleopter', 'Diptera']]
assert (parse_rec(tree_parser.parse_string('(Nematoda, (Coleoptera:siblings, Diptera))').find(TaxonList))) == ['Nematoda', ['Diptera', 'Hymenoptera', 'Siphonaptera', 'Mecoptera', 'Strepsiptera', 'Amphiesmenoptera', 'Neuropterida', 'Diptera']]

# some real queries

# what is the sister taxon to coleoptera?
print(parse_rec(tree_parser.parse_string('(Coleoptera, Coleoptera:siblings)').find(TaxonList)))

#What are the relationships between members of Endopterygota?
print(parse_rec(tree_parser.parse_string('(Endopterygota:children)').find(TaxonList)))

#What are the relationships between Amphiesmenoptera, Coleoptera, Diptera, Hymenoptera, Mecoptera, Neuropterida, Siphonaptera and Strepsiptera?
print(parse_rec(tree_parser.parse_string('(Amphiesmenoptera, Coleoptera, Diptera, Hymenoptera, Mecoptera, Neuropterida, Siphonaptera, Strepsiptera)').find(TaxonList)))



