import json
import rdflib
from rdflib import *
from rdflib.namespace import *
from rdflib.util import *
from rdflib.plugins.sparql import *
import requests
from requests_futures.sessions import FuturesSession
from concurrent.futures import as_completed
import sys
import time

# Knowledge Graph variables and namespace declaration
dbp = Namespace("http://dbpedia.org/resource/")
g = Graph()
nsm = NamespaceManager(g)
nsm.bind('dbr', 'http://dbpedia.org/resource/')
nsm.bind('ex', 'http://example.org/')
nsm.bind('focu', 'http://focu.io/schema#')
course_counter = 0
list_of_graph_entries = []
list_of_indexes_of_resourceless_courses = []
list_of_valid_graph_entries = []








###################### BELOW IS GRAPH CREATION ###########################
# Import all courses from Concordia
# file = open('final_copy.txt', 'r')
# lines = file.readlines()
# file.close()

# # Parse imported courses
# for line in lines:
# 	temp = json.loads(line)
	
# 	# COURSE
# 	course_id = list(temp.keys())[0] 
# 	title = temp[course_id]['title'] # Title (String)
# 	subject = temp[course_id]['subject'] # Subject (String)
# 	catalog = temp[course_id]['catalog'] # Catalog (int)
# 	career = temp[course_id]['career'] # Career (String)
# 	description = temp[course_id]['description'] # Description (String)
	# subject_catalog = from_n3('ex:' + subject + catalog, nsm=nsm)

# 	course_data = {
# 		"subject_catalog": subject_catalog,
# 		"title": title,
# 		"subject": subject,
# 		"catalog": catalog,
# 		"career": career,
# 		"description": description
# 	}

# 	# Dbpedia spotlight API variables and paths
# 	base_url = "http://localhost:2222/rest"
# 	api_annotate = "/annotate"
# 	header = {'accept': "application/json"}
# 	params = {"text": title + "," + description}
	
# 	# DBPEDIA SPOTLIGHT API CALLS; while loop until all courses have obtain their TOPICS
# 	while True:
# 		dbpedia_spotlight_response = requests.get(base_url+api_annotate, headers=header, params=params)
# 		# Sleep for 60seconds if API requests get blocked
# 		if dbpedia_spotlight_response.status_code != 200:
# 			print("Blocked")
# 			time.sleep(60)
# 		else:
# 			ite_num = str(course_counter) + "/" + str(len(lines))
# 			precent = float(course_counter / len(lines))
# 			hashes = '#' * int(round(precent * 20))
# 			spaces = ' ' * (20 - len(hashes))
# 			sys.stdout.write("\r[{0}]{1}%  [{2}]".format(hashes + spaces, int(round(precent * 100)), ite_num))
# 			sys.stdout.flush()
# 			break

# 	# Dbpedia spotlight API response parsing
# 	dbpedia_spotlight_string = dbpedia_spotlight_response.content.decode("utf-8")
# 	dbpedia_spotlight_dict = json.loads(dbpedia_spotlight_string)
# 	topics = []

# 	# Update course with TOPICS returned from Dbpedia spotlight
# 	# If response HAS a Resource key, populate topics list and then add to course_data{}
# 	if "Resources" in dbpedia_spotlight_dict:
# 		for list_item in dbpedia_spotlight_dict['Resources']:
# 			for dict_item_key, dict_item_value in list_item.items():
# 				if dict_item_key == '@URI':
# 					uri_ref = URIRef(dict_item_value)
# 					topics.append(uri_ref)
# 					break
# 		course_data.update({'topics': topics})
# 		list_of_valid_graph_entries.append(course_data)

# 	# If response DOESN'T HAVE a Resource key, save index - to be populated later.
# 	else:
# 		course_data.update({'topics': "NO RESOURCES"})
# 		list_of_indexes_of_resourceless_courses.append(course_counter)

# 	list_of_graph_entries.append(course_data)
# 	course_counter += 1
# 	# if course_counter == 50:
# 	# 	break

# # for ent in list_of_indexes_of_resourceless_courses:
# # 	print(list_of_graph_entries[ent])

# # print("")
# # print(len(list_of_indexes_of_resourceless_courses), " courses with missing Resources from Dbpedia Spotlight")



# # TODO: Add all COURSES from list_of_graph_entries to graph g
# for entry in list_of_valid_graph_entries:
# 	subject_catalog = entry['subject_catalog']
# 	title = entry['title']
# 	subject = entry['subject']
# 	catalog = entry['catalog']
# 	description = entry['description']

# 	# g.add((subject_catalog, from_n3('focu:course_id', nsm=nsm), Literal(course_id)))
# 	g.add((subject_catalog, RDF.type, from_n3('dbr:Course_(education)', nsm=nsm)))
# 	g.add((subject_catalog, RDFS.label, Literal(title)))
# 	g.add((subject_catalog, from_n3('focu:subject', nsm=nsm), Literal(subject)))
# 	g.add((subject_catalog, from_n3('focu:catalog', nsm=nsm), Literal(catalog)))
# 	g.add((subject_catalog, RDFS.comment, Literal(description)))
# 	for uri_ref in entry['topics']:
# 		g.add((subject_catalog, FOAF.topic, uri_ref))

###################### END OF GRAPH CREATION ###########################


student_1 = ["1", "Sean1", "Neas1", "sean1@123.com", [["2000", "AERO371", "B"], ["2001", "ELEC372", "C"]]]
student_2 = ["2", "Sean2", "Neas2", "sean2@123.com", [["2000", "ENGL246", "F"], ["2001", "ENGL350", "D"]]]

students = [student_1, student_2]



record_counter = 1

for student in students:
	_student = from_n3('ex:' + student[0] , nsm=nsm)
	g.add((_student, RDF.type, from_n3('focu:student', nsm=nsm)))
	g.add((_student, FOAF.firstName, Literal(student[1])))
	g.add((_student, FOAF.lastName, Literal(student[2])))
	g.add((_student, FOAF.mbox, Literal(student[3])))
	for records in student[4]:
		_record = from_n3('ex:record' + str(record_counter), nsm=nsm)
		g.add((_student, from_n3('focu:hasRecord', nsm=nsm), _record))
		g.add((_record, from_n3('focu:semester', nsm=nsm), Literal(records[0])))
		g.add((_record, from_n3('focu:subject_catalog', nsm=nsm), from_n3('ex:' + records[1], nsm=nsm)))
		g.add((_record, from_n3('focu:grade', nsm=nsm), Literal(records[2])))
		record_counter += 1


	# g.add((subject_catalog, from_n3('focu:course_id', nsm=nsm), Literal(course_id)))
	# subject_catalog = from_n3('ex:' + subject + catalog, nsm=nsm)



query_agent = g.query(
	"""SELECT ?s ?p ?o
		WHERE {		
			?s rdf:type ?o .
			?s foaf:firstName ?p .
		}
	""")

for each_row in query_agent:
	print(each_row)



# serialized_graph = g.serialize(format='turtle')

# with open('test_graph.txt', 'w') as file:
# 	file.write(serialized_graph.decode())


# for s, p, o in g:
# 	print(s, p, o)
