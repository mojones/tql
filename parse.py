from modgrammar import *
import tax

class TaxonName (Grammar):
	grammar = (WORD("A-Za-z "))

class TaxonExtension (Grammar):
	grammar = (L("children") | L("parent") | L("siblings"))

class TaxonFull (Grammar):
	grammar = ( TaxonName, OPTIONAL(':', TaxonExtension) )


class TaxonList (Grammar):
	grammar = ('(' , LIST_OF(TaxonFull, sep=",") , ')' )



def get_taxon_list(input):
	taxon_list_parser = TaxonList.parser()
	taxon_list_result = taxon_list_parser.parse_string(input)
	result = []
	for taxon in taxon_list_result.find_all(TaxonFull):
		taxon_name = taxon.elements[0].string
		taxon_extension = taxon.elements[1]
		print(repr(taxon))
		# if the extension is none, then just add the name 
		if taxon_extension == None:
			result.append(taxon_name)
		else:
			print(taxon_extension)
			# deal with children
			if taxon_extension.string == ':children':
				result.extend(tax.get_children(taxon_name))
			if taxon_extension.string == ':parent':
				result.append(tax.get_parent(taxon_name))
			if taxon_extension.string == ':siblings':
				result.extend(tax.get_siblings(taxon_name))


	return result

print(get_taxon_list('(nematoda)'))
print(get_taxon_list('(nematoda, arthropoda, sea spiders)'))
print(get_taxon_list('(Nematoda:children, arthropoda, sea spiders)'))
print(get_taxon_list('(Coleoptera:parent, Nematoda, Eutheria)'))
print(get_taxon_list('(Coleoptera:siblings)'))

