import json
from rdflib import *
from rdflib.namespace import *
from rdflib.util import *
import requests, ast

dbp = Namespace("http://dbpedia.org/resource/")

g = Graph()

nsm = NamespaceManager(g)
nsm.bind('dbr', 'http://dbpedia.org/resource/')
nsm.bind('ex', 'http://example.org/')
nsm.bind('focu', 'http://focu.io/schema#')

file = open('final_copy.txt', 'r')
lines = file.readlines()
iterator = 0
for line in lines:
		
	temp = json.loads(line)

	# COURSE
	title_id = list(temp.keys())[0] 
	title = temp[title_id]['title'] # Title (String)
	subject = temp[title_id]['subject'] # Subject (String)
	catalog = temp[title_id]['catalog'] # Catalog (int)
	career = temp[title_id]['career'] # Career (String)
	description = temp[title_id]['description'] # Description (String)


	base_url = "https://api.dbpedia-spotlight.org/en/"
	header = {'accept': "application/json"}
	params = {"text": title + "," + description}
	
	dbpedia_spotlight_response = requests.get(base_url+"annotate", headers=header, params=params)
	dbpedia_spotlight_string = dbpedia_spotlight_response.content.decode("utf-8")
	dbpedia_spotlight_dict = json.loads(dbpedia_spotlight_string)
	for key in dbpedia_spotlight_dict:
		print (key)		


	# print(title)
	# print(subject)
	# print(catalog)
	# print(career)
	# print(description)
	# print(topics)
	
	subject_catalog = from_n3('ex:' + subject + catalog, nsm=nsm)

	g.add((subject_catalog, RDF.type, from_n3('dbr:Course_(education)', nsm=nsm)))
	g.add((subject_catalog, RDFS.label, Literal(title)))
	g.add((subject_catalog, from_n3('focu:subject', nsm=nsm), Literal(subject)))
	g.add((subject_catalog, from_n3('focu:catalog', nsm=nsm), Literal(catalog)))
	g.add((subject_catalog, RDFS.comment, Literal(description)))

	iterator += 1
	if (iterator == 5):
		break


# for s, p, o in g:
# 	print(s, p, o)







