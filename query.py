import re
from rdflib import Graph, URIRef, Literal
from rdflib.namespace import FOAF, RDF
from rdflib.plugins.sparql import prepareQuery


###################################### QUERY LOOP ####################################################################
if __name__ == '__main__':
	g = Graph()
	result = g.parse("knowledge_base.txt", format="turtle")

	
	
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
