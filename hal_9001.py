import spacy
import re
from rdflib import Graph, URIRef, Literal
from rdflib.namespace import FOAF, RDF
from rdflib.plugins.sparql import prepareQuery


g = Graph()
result = g.parse("knowledge_base.txt", format="turtle")
nlp = spacy.load("en_core_web_md")  # make sure to use larger model!
question_1 = nlp("What is about?")
question_2 = nlp("Which courses did take")
question_3 = nlp("Which courses cover")
question_4 = nlp("Who is familiar with")
match=False

def determine_question(input_text):
	"""
	Uses NLP to determine with 80% certainty which question is being asked
	"""	
	text_doc = nlp(input_text)
	for token in text_doc:
		if token.lower_ in ["about"]:
			question_similarity = text_doc.similarity(question_1)
			if question_similarity > 0.80:	
				# print("[", text_doc.text, "|", question_1.text, "]", question_similarity)
				course = re.match(r'.* is (.*) about', input_text)
				if course==None:
					print("Hal_9001 > Your question does not make sense... Try again, human.")
					match=True
				else:
					return("question_1", course.group(1))
		elif token.lower_ in ["take"]:
			question_similarity = text_doc.similarity(question_2)
			if question_similarity > 0.80:	
				# print("[", text_doc.text, "|", question_2.text, "]", question_similarity)
				student = re.match(r'.* did (.*) take', input_text)
				if student==None:
					print("Hal_9001 > Your question does not make sense... Try again, human.")
					match=True
				else:
					return("question_2", student.group(1))
		elif token.lower_ in ["cover"]:
			question_similarity = text_doc.similarity(question_3)
			if question_similarity > 0.80:	
				# print("[", text_doc.text, "|", question_3.text, "]", question_similarity)
				topic = re.match(r'.* cover (.*)', input_text)
				if topic==None:
					print("Hal_9001 > Your question does not make sense... Try again, human.")
					match=True
				else:
					return("question_3", topic.group(1))
		elif token.lower_ in ["familiar"]:
			question_similarity = text_doc.similarity(question_4)
			if question_similarity > 0.80:	
				# print("[", text_doc.text, "|", question_4.text, "]", question_similarity)
				familiar_topic = re.match(r'.* with (.*)', input_text)
				if familiar_topic==None:
					print("Hal_9001 > Your question does not make sense... Try again, human.")
					match=True
				else:
					return("question_4", familiar_topic.group(1))	
	return("null", "null")


def query_knowledge_graph(question_type, question_details):
	"""
	Query knowledge graph by create an appropriate SPARQL-query format depending on the question_type
	"""

	# QUESTION 1
	if question_type is "question_1":
		# question_details holds course name; return all topics related	
		c_sub_cata = question_details
		target = URIRef("http://example.org/" + c_sub_cata)
		q_topic = prepareQuery(
			"""SELECT ?topic WHERE {
				?c_sub_cata foaf:topic ?topic
			}""",
			initNs = {
				"c_sub_cata": target, "foaf": FOAF, "rdf":RDF, "focu":"http://focu.io/schema#"			
			}
		)
		print("Hal_9001 > " + question_details + " is (potentially) about:")	
		for row in g.query(q_topic, initBindings={"c_sub_cata": target}):
			topic_label = re.match(r'.*/resource/(.*)', str(row[0]))
			print(" 	", topic_label.group(1).replace("_", " "))

	# QUESTION 2			
	elif question_type is "question_2":
		# question_details holds Student ID; return courses Student has completed
		student_id = question_details
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
		print("Hal_9001 > Student " + student_id + " has taken the following courses:")
		for row in g.query(q, initBindings={"s_id": target}):
			pretty_row = (" 	%s %s %s" % row).replace("http://example.org/", "")
			print(pretty_row)

	# QUESTION 3
	elif question_type is "question_3":
		# question_details holds a Topic; return courses covering said Topic
		# TODO!
		target = URIRef("http://dbpedia.org/resource/" + question_details)
		q_topic = prepareQuery(
				"""SELECT ?c_sub_cata WHERE {
					?c_sub_cata foaf:topic ?topic
				}""",
				initNs = {
					"topic": target, "foaf": FOAF, "rdf":RDF, "focu":"http://focu.io/schema#"			
				}
			)
		label_subject_list=[]
		for row in g.query(q_topic, initBindings={"topic": target}):
			print(row)

	# QUESTION 4
	elif question_type is "question_4":
		# question_details holds a Topic; return students familiar with said Topic
		topic_of_interest = question_details.replace(" ", "_")
		topic_of_interest = topic_of_interest.replace("?", "")
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
			pretty_row = row[0].replace("http://example.org/", "")
			print(" 	", pretty_row)


if __name__ == '__main__':
	print("Hal_9001 > Greetings human, my name is Hal 9001. How may I assist you?")
	while True:
		try:
			question_type, question_details = determine_question(input("User > "))
			if question_type is not "null" and question_details is not "null":
				query_knowledge_graph(question_type, question_details)
			else:
				if not match:
					print("Hal_9001 > Your question has no answer... Try again, human.")
				else:
					match=False	
		except KeyboardInterrupt:
			print("Hal_9001 > Your question does not make sense... Try again, human.")
			break












