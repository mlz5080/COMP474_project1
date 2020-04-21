import spacy


nlp = spacy.load("en_core_web_md")  # make sure to use larger model!
question_1 = nlp("What is about?")
question_2 = nlp("Which course did take")
question_3 = nlp("Which courses cover")
question_4 = nlp("Who is familiar with")


def determine_question(input_text):
	"""
	Uses NLP to determine with 80% certainty which question is being asked
	"""	
	text_doc = nlp(input_text)
	for token in text_doc:
		if token.lower_ in ["about"]:
			question_similarity = text_doc.similarity(question_1)
			if question_similarity > 0.80:	
				print(text_doc.text, question_1.text, question_similarity)
				course = re.match(r'.* is (.*) about')
				print(course)
				break
		elif token.lower_ in ["take"]:
			question_similarity = text_doc.similarity(question_2)
			if question_similarity > 0.80:	
				print(text_doc.text, question_2.text, question_similarity)
				break
		elif token.lower_ in ["cover"]:
			question_similarity = text_doc.similarity(question_3)
			if question_similarity > 0.80:	
				print(text_doc.text, question_3.text, question_similarity)
				break
		elif token.lower_ in ["familiar"]:
			question_similarity = text_doc.similarity(question_4)
			if question_similarity > 0.80:	
				print(text_doc.text, question_4.text, question_similarity)
				break

if __name__ == '__main__':
	while True:
		determine_question(input(" > "))
















