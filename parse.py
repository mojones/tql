from modgrammar import *
import tax


def iter_flatten(iterable):
  it = iter(iterable)
  for e in it:
    if isinstance(e, (list, tuple)):
      for f in iter_flatten(e):
        yield f
    else:
      yield e


# a taxon name is upper and lower case letters plus space
# to allow for common names / binomials
class Name (Grammar):
	grammar = (WORD("A-Za-z "))

# there are three possible extensions to a taxon name
class TaxonSuffix (Grammar):
	grammar = (L("children") | L("parent") | L("siblings"))

class TaxonSuffixQuantifier (Grammar):
	grammar = (  WORD("0123456789")  )


# not used
class TaxonPrefix (Grammar):
	grammar = (L("sister"))



class Exclude (Grammar):
	grammar = ( L('-') )

# a full taxon name is a normal taxon name followed, optionally, 
# by a colon then the extension
class TaxonFull (Grammar):
	grammar = ( OPTIONAL(Exclude), Name, OPTIONAL(':', TaxonSuffix, OPTIONAL('{', TaxonSuffixQuantifier, '}')) )
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
	grammar = (  LIST_OF(Tree, sep=";")  )





def expand_taxon(taxon):
	# print(repr(taxon))
	taxon_name = taxon.find(Name).string
	suffix = taxon.find(TaxonSuffix)


	# if the extension is none, then just add the name 
	if suffix == None:
		return [taxon_name]
	
	# otherwise do something interesting
	else:

		# grab the suffix quantifier, if there is one, and turn it into an int
		suffix_quantifier = taxon.find(TaxonSuffixQuantifier)
		if suffix_quantifier == None:
			suffix_quantifier = 1
		else:
			suffix_quantifier = int(suffix_quantifier.string)

		# print(suffix)
		# deal with suffixes
		if suffix.string == 'children':
			return tax.get_children_multiple(taxon_name, suffix_quantifier)
		if suffix.string == 'parent':
			return [tax.get_parent(taxon_name)]
		if suffix.string == 'siblings':
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
		if taxon in result:
			result.remove(taxon)
	return result

def parse_trees(input_trees):
	parsed_trees = {}
	for tree in input_trees:
		tree_parser = Tree.parser()
		parsed_tree = tree_parser.parse_string(tree)
		tree_name = parsed_tree.find(Name).string
		tree_as_list = parse_rec(parsed_tree.find(TaxonList))
		parsed_trees[tree_name] = tree_as_list

	for name, tree in parsed_trees.items():
		print('##  ' + name + '  ##')
		print(tree)
		if len(set(iter_flatten(tree))) < len(list(iter_flatten(tree))):
			print('warning: some taxa occur multiple times in the tree')



# playing with negation and multi-childrening

# Coleoptera and all siblings
# parse_trees('my tree:(Coleoptera, Coleoptera:siblings);')
# Coleoptera and all siblings excluding diptera
# parse_trees('my tree:(Coleoptera, Coleoptera:siblings, -Diptera);')
# Coleoptera is closer to Diptera than to any other sibling
# parse_trees('my tree:((Coleoptera, Diptera), Coleoptera:siblings, -Diptera);')

# compare two hypotheses; coleoptera+diptera vs coleoptera + hymenoptera
# parse_trees([
# 	'hypa:((Coleoptera, Diptera), Coleoptera:siblings, -Diptera)',
# 	'hypb:((Coleoptera, Hymenoptera), Coleoptera:siblings, -Hymenoptera)'
# 	])



# parse_trees('my tree:(Mandibulata:children{1});')
# parse_trees('my tree:(Pancrustacea:children{1});')
# parse_trees('my tree:(Mandibulata:children{2});')
parse_trees(['my tree:((Mandibulata:children{2}), Crustacea)'])
# parse_trees(['my tree:(Mandibulata:children{2}, -Mandibulata:children{2})'])


