import json,random,sys,time,re, requests
from rdflib import Graph, URIRef, Literal
from rdflib.util import from_n3
from rdflib.namespace import FOAF, RDF, RDFS, Namespace, NamespaceManager
from rdflib.plugins.sparql import prepareQuery


#Knowledge Graph variable and namespace declaration
dbp = Namespace("http://dbpedia.org/resource/")
g = Graph()
result = g.parse("schema.ttl", format="turtle")
nsm = NamespaceManager(g)
nsm.bind('dbr', 'http://dbpedia.org/resource/')
nsm.bind('ex', 'http://example.org/')
nsm.bind('focu', 'http://focu.io/schema#')
course_counter = 0
list_of_indexes_of_resourceless_courses = []
list_of_valid_graph_entries = []
concordia_university = URIRef('http://example.org/Concordia')
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
	
	#Step 1: Extract relevant entries from each database.txt datapoint
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
	#End of Step 1

	# Dbpedia spotlight API variables and paths
	base_url = "http://localhost:2222/rest"
	api_annotate = "/annotate"
	api_candidate = "/candidate"
	header = {'accept': "application/json"}
	params = {"text": title + "," + description}
	
	#Step 2: Obtain Topics related to each course
	# DBPEDIA SPOTLIGHT API CALLS; while loop until course has obtain all TOPICS
	while True:
		dbpedia_spotlight_response = requests.get(base_url+api_annotate, headers=header, params=params)
		# Sleep for 60seconds if API requests get blocked
		if dbpedia_spotlight_response.status_code != 200:
			print("Blocked")
			time.sleep(60)
		else:
			ite_num = str(course_counter) + "/" + str(len(lines)-1)
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
	#End of Step 2

	# DEBUGGING LIMIT
	# if course_counter == 25:
	# 	break
	############## END OF DBP RESPONSE PARSING ##############

#Step 3: 
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
	g.add((subject_catalog, from_n3('focu:offeredAt', nsm=nsm), concordia_university))
	for uri_ref in entry['topics']:
		g.add((subject_catalog, FOAF.topic, uri_ref))
		# topic = re.match(r'.*/resource/(.*)', uri_ref)
		# print(topic.group(1).replace("_", " "))
		# params = {"text": topic}
		# dbpedia_spotlight_response = requests.get(base_url+api_candidate, headers=header, params=params)
		# print("RESPONSE: ", dbpedia_spotlight_response)
#End of Step 3
#GRAPH CREATED!
###################################### END OF GRAPH CREATION #########################################################

#Generate bank of random students
#Step 4: Generating Students and adding them to Knowledge Graph
random_students = create_students()

###################################### Create Student and add to g graph ####################################
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

g.serialize(destination='knowledge_base.txt', format='turtle')
g.serialize(destination='knowledge_base_n3.txt', format='nt')
#End of Step 4
###################################### End of Student addition to graph #####################################
