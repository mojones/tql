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
	print(repr(taxon))
	taxon_name = taxon.elements[0].string
	taxon_extension = taxon.elements[1]
	# if the extension is none, then just add the name 
	if taxon_extension == None:
		return [taxon_name]
	else:
		print(taxon_extension)
		# deal with children
		if taxon_extension.string == ':children':
			return (tax.get_children(taxon_name))
		if taxon_extension.string == ':parent':
			return [tax.get_parent(taxon_name)]
		if taxon_extension.string == ':siblings':
			return tax.get_siblings(taxon_name)

def expand_list(list):
	result = []
	for taxon in list.find_all(TaxonFull):
		result.extend(expand_taxon(taxon))
	return result

def list_subtrees(tree, level = 0):
	if tree == None:
		return
	for subtree in tree.find_tag_all("list element"):
		print('   ' * level + repr(subtree))
		list_subtrees(subtree, level+1)


def list_subtrees(tree, level = 0):
	if tree == None:
		return
	for subtree in tree.find_tag_all("list element"):
		print('   ' * level + repr(subtree))
		list_subtrees(subtree, level+1)






# print(get_taxon_list('(nematoda)'))
# print(get_taxon_list('(nematoda, arthropoda, sea spiders)'))
# print(get_taxon_list('(Nematoda:children, arthropoda, sea spiders)'))
# print(get_taxon_list('(Coleoptera:parent, Nematoda, Eutheria)'))
# print(get_taxon_list('(Coleoptera:siblings)'))

test_tree = tree_parser.parse_string('(alpha, (beta, gamma), delta)')
list_subtrees(test_tree)

