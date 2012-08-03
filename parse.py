from modgrammar import *
import tax

# a taxon name is upper and lower case letters plus space
# to allow for common names / binomials
class Name (Grammar):
	grammar = (WORD("A-Za-z "))

# there are three possible extensions to a taxon name
class TaxonSuffix (Grammar):
	grammar = (L("children") | L("parent") | L("siblings"))

class TaxonPrefix (Grammar):
	grammar = (L("sister"))

class Exclude (Grammar):
	grammar = ( L('-') )

# a full taxon name is a normal taxon name followed, optionally, 
# by a colon then the extension
class TaxonFull (Grammar):
	grammar = ( OPTIONAL(Exclude), Name, OPTIONAL(':', TaxonSuffix) )
	grammar_tags = ("list element",)

# a TaxonList starts and ends with brackets
# inside the brackets is a list separated by commas
# each element of the list is either a full taxon name or another list
class TaxonList (Grammar):
	grammar = (  '(' , LIST_OF(OR(TaxonFull, REF('TaxonList')), sep=",") , ')'  )
	grammar_tags = ("list element",)

# a tree contains a top-level taxon list
class Tree (Grammar):
	grammar = ( Name, ':', TaxonList  )

class TreeList (Grammar):
	grammar = (  ONE_OR_MORE(Tree, sep=";")  )


tree_list_parser = TreeList.parser()



def expand_taxon(taxon):
	# print(repr(taxon))
	taxon_name = taxon.find(Name).string
	taxon_extension = taxon.find(TaxonSuffix)
	# if the extension is none, then just add the name 
	if taxon_extension == None:
		return [taxon_name]
	else:
		# print(taxon_extension)
		# deal with children
		if taxon_extension.string == 'children':
			return tax.get_children(taxon_name)
		if taxon_extension.string == 'parent':
			return [tax.get_parent(taxon_name)]
		if taxon_extension.string == 'siblings':
			return tax.get_siblings(taxon_name)


def list_subtrees(tree, level = 0):
	if tree == None:
		return
	for subtree in tree.find_tag_all("list element"):
		print('   ' * level + repr(subtree))
		list_subtrees(subtree, level+1)


def parse_rec(tree, level = 0):
	result = []
	to_remove = []
	for subtree in tree.find_tag_all("list element"):
		if isinstance(subtree, TaxonFull):
			if subtree.find(Exclude):
				to_remove.extend(expand_taxon(subtree))
			else:
				result.extend(expand_taxon(subtree))
		if isinstance(subtree, TaxonList):
			result.append(parse_rec(subtree))
	for taxon in to_remove:
		result.remove(taxon)
	return result

def parse_trees(input):

	parsed = tree_list_parser.parse_string(input)

	print(repr(parsed))
	parsed_trees = {}
	for tree in parsed.elements:
		print(repr(tree))
		tree_name = tree.find(Name)
		list = parse_rec(tree.find(TaxonList))
		parsed_trees[tree_name] = list

	print(parsed_trees)

# some tests to make sure we don't break anything

# test flat lists of simple names
# assert (parse_rec(tree_parser.parse_string('my tree:(nematoda)').find(TaxonList))) == ['nematoda']
# assert (parse_rec(tree_parser.parse_string('my tree:(nematoda, arthropoda, sea spiders)').find(TaxonList))) == ['nematoda', 'arthropoda', 'sea spiders']

# # test children, sibling, parent extensions
# assert (parse_rec(tree_parser.parse_string('my tree:(Nematoda:children, arthropoda, sea spiders)').find(TaxonList))) == ['unclassified Nematoda', 'Enoplea', 'Chromadorea', 'Nematoda environmental samples', 'arthropoda', 'sea spiders']
# assert (parse_rec(tree_parser.parse_string('my tree:(Coleoptera:parent, Nematoda, Eutheria)').find(TaxonList))) == ['Endopterygota', 'Nematoda', 'Eutheria']
# assert (parse_rec(tree_parser.parse_string('my tree:(Coleoptera:siblings)').find(TaxonList))) == ['Diptera', 'Hymenoptera', 'Siphonaptera', 'Mecoptera', 'Strepsiptera', 'Amphiesmenoptera', 'Neuropterida']

# # test structured trees with simple names
# assert (parse_rec(tree_parser.parse_string('my tree:(Nematoda, (Tardigrada, Coleoptera))').find(TaxonList))) == ['Nematoda', ['Tardigrada', 'Coleoptera']]
# assert (parse_rec(tree_parser.parse_string('my tree:(Nematoda, (Tardigrada, (Homo, Pan), Coleoptera))').find(TaxonList))) == ['Nematoda', ['Tardigrada', ['Homo', 'Pan'], 'Coleoptera']]

# # test structured trees with extensions
# assert (parse_rec(tree_parser.parse_string('my tree:(Nematoda:children, (Coleopter, Diptera))').find(TaxonList))) == ['unclassified Nematoda', 'Enoplea', 'Chromadorea', 'Nematoda environmental samples', ['Coleopter', 'Diptera']]
# assert (parse_rec(tree_parser.parse_string('my tree:(Nematoda, (Coleoptera:siblings, Diptera))').find(TaxonList))) == ['Nematoda', ['Diptera', 'Hymenoptera', 'Siphonaptera', 'Mecoptera', 'Strepsiptera', 'Amphiesmenoptera', 'Neuropterida', 'Diptera']]

# some real queries

# what is the sister taxon to coleoptera?
#print(parse_rec(tree_parser.parse_string('my tree:(Coleoptera, Coleoptera:siblings)').find(TaxonList)))

#What are the relationships between members of Endopterygota?
# print(parse_rec(tree_parser.parse_string('my tree:(Endopterygota:children)').find(TaxonList)))

#What are the relationships between Amphiesmenoptera, Coleoptera, Diptera, Hymenoptera, Mecoptera, Neuropterida, Siphonaptera and Strepsiptera?
# print(parse_rec(tree_parser.parse_string('my tree:(Amphiesmenoptera, Coleoptera, Diptera, Hymenoptera, Mecoptera, Neuropterida, Siphonaptera, Strepsiptera)').find(TaxonList)))

# are arthropods monophyletic?
# print(parse_rec(tree_parser.parse_string('my tree:((Arthropoda:children), Arthropoda:siblings)').find(TaxonList)))

parse_trees('my tree:(Coleoptera, Coleoptera:siblings, -Diptera);')


