import json,random,sys,time,re, requests
from rdflib import Graph, URIRef, Literal
from rdflib.util import from_n3
from rdflib.namespace import FOAF, RDF, RDFS, Namespace, NamespaceManager
from concurrent.futures import as_completed
from rdflib.plugins.sparql import prepareQuery
from requests_futures.sessions import FuturesSession


#Knowledge Graph variable and namespace declaration
dbp = Namespace("http://dbpedia.org/resource/")
g = Graph()
result = g.parse("namespace.xml", format="xml")
nsm = NamespaceManager(g)
nsm.bind('dbr', 'http://dbpedia.org/resource/')
nsm.bind('ex', 'http://example.org/')
nsm.bind('focu', 'http://focu.io/schema#')
course_counter = 0
list_of_indexes_of_resourceless_courses = []
list_of_valid_graph_entries = []
#End of variable and namespace declaration

def create_students():
	"""
	Generate 100 "dummy" students. Each student has between 4-40 records (aka courses with an associated grade and semester)
	:return:
	"""
	student_list = []
	firstname = "Sean"
	lastname = "Neas"
	grade_list = ["A","B","C","D","F"]
	total_valid_class = len(list_of_valid_graph_entries)
	for uid in range(1,101):
		uid_str=str(uid)
		stu_firstname=firstname+uid_str
		stu_lastname=lastname+uid_str
		email = (firstname+uid_str).lower()+"@123.com"
		course_number = random.randint(4,40)
		records_list=[]
		for record_index in range(course_number):
			year = str(random.randint(1990,2021))
			course_index = random.randint(0,total_valid_class-1)
			course = list_of_valid_graph_entries[course_index]
			record = [year,course['subject']+course['catalog'],grade_list[random.randint(0,4)]]
			records_list.append(record)
		student=[uid_str,stu_firstname,stu_lastname,email,records_list]
		student_list.append(student)
	return student_list
#End of create_students()


###################################### BELOW IS GRAPH CREATION #######################################################
# Import all courses generated from database_builder.py --> database.txt
file = open('database.txt', 'r')
lines = file.readlines()
file.close()

# Parse imported courses
for line in lines:
	temp = json.loads(line)
	
	# COURSE INFORMATION
	course_id = list(temp.keys())[0] 
	title = temp[course_id]['title'] # Title (String)
	subject = temp[course_id]['subject'] # Subject (String)
	catalog = temp[course_id]['catalog'] # Catalog (int)
	career = temp[course_id]['career'] # Career (String)
	description = temp[course_id]['description'] # Description (String)
	subject_catalog = from_n3('ex:' + subject + catalog, nsm=nsm)

	# Create course dict to store important values
	course_data = {
		"subject_catalog": subject_catalog,
		"title": title,
		"subject": subject,
		"catalog": catalog,
		"career": career,
		"description": description
	}

	# Dbpedia spotlight API variables and paths
	base_url = "http://localhost:2222/rest"
	api_annotate = "/annotate"
	header = {'accept': "application/json"}
	params = {"text": title + "," + description}
	
	# DBPEDIA SPOTLIGHT API CALLS; while loop until course has obtain all TOPICS
	while True:
		dbpedia_spotlight_response = requests.get(base_url+api_annotate, headers=header, params=params)
		# Sleep for 60seconds if API requests get blocked
		if dbpedia_spotlight_response.status_code != 200:
			print("Blocked")
			time.sleep(60)
		else:
			ite_num = str(course_counter) + "/" + str(len(lines))
			precent = float(course_counter / len(lines))
			hashes = '#' * int(round(precent * 20))
			spaces = ' ' * (20 - len(hashes))
			sys.stdout.write("\r[{0}]{1}%  [{2}]".format(hashes + spaces, int(round(precent * 100)), ite_num))
			sys.stdout.flush()
			break

	########## DBPEDIA SPOTLIGHT RESPONSE PARSING ###########
	dbpedia_spotlight_string = dbpedia_spotlight_response.content.decode("utf-8")
	dbpedia_spotlight_dict = json.loads(dbpedia_spotlight_string)
	topics = []

	# Update course with TOPICS returned from Dbpedia spotlight
	# If response HAS a Resource key, populate topics list and then add to course_data{}
	if "Resources" in dbpedia_spotlight_dict:
		for list_item in dbpedia_spotlight_dict['Resources']:
			for dict_item_key, dict_item_value in list_item.items():
				if dict_item_key == '@URI':
					uri_ref = URIRef(dict_item_value)
					topics.append(uri_ref)
					break
		course_data.update({'topics': topics})
		list_of_valid_graph_entries.append(course_data)

	# If response DOESN'T HAVE a Resource key, save index - to be populated later.
	else:
		course_data.update({'topics': "NO RESOURCES"})
		list_of_indexes_of_resourceless_courses.append(course_counter)
	course_counter += 1

	# DEBUGGING LIMIT
	# if course_counter == 25:
	# 	break
	############## END OF DBP RESPONSE PARSING ##############


# Add all COURSES from list_of_valid_graph_entries to graph g
for entry in list_of_valid_graph_entries:
	subject_catalog = entry['subject_catalog']
	title = entry['title']
	subject = entry['subject']
	catalog = entry['catalog']
	description = entry['description']
	g.add((subject_catalog, RDF.type, from_n3('dbr:Course_(education)', nsm=nsm)))
	g.add((subject_catalog, RDFS.label, Literal(title)))
	g.add((subject_catalog, from_n3('focu:subject', nsm=nsm), Literal(subject)))
	g.add((subject_catalog, from_n3('focu:catalog', nsm=nsm), Literal(catalog)))
	g.add((subject_catalog, RDFS.comment, Literal(description)))
	for uri_ref in entry['topics']:
		g.add((subject_catalog, FOAF.topic, uri_ref))

#GRAPH CREATED!
###################################### END OF GRAPH CREATION #########################################################

#Generate bank of random students
random_students = create_students()

###################################### Create Student node and add to g graph ###############################
record_counter = 1
for student in random_students:
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
print("\n")
###################################### End of Student addition to graph #####################################


###################################### QUERY LOOP ####################################################################
while True:
	query_type = input("\nEnter 1 for number of triple in Knowledge Base"
						"\nEnter 2 for total number of students, courses and topics"
						"\nEnter 3 for all topics related to a given course"
						"\nEnter 4 for all completed courses for a given student"
						"\nEnter 5 for all students familiar with a given topic"
						"\nEnter 6 for all topics familiar to a given student"
						"\n > ")
	#QUESTION 1
	if query_type is "1":
		print("Number of triple(s) in Knowledge Base: ", len(g))
	#QUESTION 2
	elif query_type is "2":
		# FIND COUNT OF STUDENTS
		q = g.query(
			"""SELECT (COUNT(*) AS ?count)
				WHERE {		
					?s rdf:type focu:student .
				}
			""")
		for row in q:
			print("%s Students" % row)
		# FIND COUNT OF COURSES
		q = g.query(
			"""SELECT (COUNT(*) AS ?count)
				WHERE {		
					?s rdf:type <http://dbpedia.org/resource/Course_(education)> .
				}
			""")
		for row in q:
			print("%s Courses" % row)
		# FIND COUNT OF TOPICS
		topics_list = []
		q = g.query(
			"""SELECT DISTINCT ?o
				WHERE {		
					?s foaf:topic ?o .
				}
				GROUP BY ?o
			""")
		for row in q:
			topic_of_row = row[0]
			if topic_of_row not in topics_list:
				topics_list.append(topic_of_row)
		print(len(topics_list), " Topics")
	#QUESTION 3
	elif query_type is "3":
		course_sub_cata = input("Please enter the Subject Catalog (i.e. ACCO435) of a Course"
								"\n > ")
		target = URIRef("http://example.org/" + course_sub_cata)
		q_topic = prepareQuery(
			"""SELECT ?topic WHERE {
				?c_sub_cata foaf:topic ?topic
			}""",
			initNs = {
				"c_sub_cata": target, "foaf": FOAF, "rdf":RDF, "focu":"http://focu.io/schema#"			
			}
		)
		label_topic_list = []
		for row in g.query(q_topic, initBindings={"c_sub_cata": target}):
			topic_label = re.match(r'.*/resource/(.*)', str(row[0]))
			print("\n- Topic Label:")
			print(topic_label.group(1).replace("_", " "))
			print("- Dbpedia URL:\n", row[0])
	#QUESTION 4
	elif query_type is "4":
		student_id = input("Please enter the ID of a given Student"
							"\n > ")
		target = URIRef("http://example.org/" + student_id)
		q = prepareQuery(
				"""SELECT ?sem ?sc ?g  WHERE {
					?s_id focu:hasRecord ?rec .
					?rec focu:semester ?sem .
					?rec focu:subject_catalog ?sc .
					?rec focu:grade ?g .
				}""",
				initNs = {
					"s_id": target, "foaf": FOAF, "rdf":RDF, "focu":"http://focu.io/schema#"
				}
			)
		print("Complete Courses for [Student " + student_id + "]")
		for row in g.query(q, initBindings={"s_id": target}):
			if str(row[2]) != "F":
				print("%s %s %s" % row)
	#QUESTION 5
	elif query_type is "5":
		topic_of_interest = input("Please enter the topic of interest"
									"\n > ")
		topic_of_interest = topic_of_interest.replace(" ", "_")
		target = URIRef("http://dbpedia.org/resource/" + topic_of_interest)
		q = prepareQuery(
			"""SELECT ?student WHERE {
				?sub_cata foaf:topic ?tar .
				?record focu:subject_catalog ?sub_cata .
				?record focu:grade ?grade .
				FILTER(?grade != "F") .
				?student focu:hasRecord ?record
			}""",
			initNs = {
				"tar": target, "dbp": "http://dbpedia.org/resource/" , "foaf": FOAF, "rdf":RDF, "focu":"http://focu.io/schema#"
			}
		)
		for row in g.query(q, initBindings={"tar": target}):
			print(row[0])
	#QUESTION 6
	elif query_type is "6":
		student_id = input("Please enter the ID of a given student"
							"\n > ")
		target = URIRef("http://example.org/" + student_id)
		q = prepareQuery(
				"""SELECT ?topic WHERE {
					?s_id focu:hasRecord ?rec .
					?rec focu:grade ?g .
					?rec focu:subject_catalog ?sc .
					?sc foaf:topic ?topic
				}""",
				initNs = {
					"s_id": target, "foaf": FOAF, "rdf":RDF, "focu":"http://focu.io/schema#"
				}
			)
		for row in g.query(q, initBindings={"s_id": target}):
			print("%s" % row)
###################################### END OF LOOP QUERY ############################################################################
