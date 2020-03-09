import requests,ast
from requests_futures.sessions import FuturesSession
from concurrent.futures import as_completed
import json
import copy
from bs4 import BeautifulSoup
import re


#API autentication variables declaration
User="124"
Key="d3c1c8924a8d59f9b5f29f54bbbbb5e7"
print("Builder launched [...]")
#API format
#Any parameter could be replaced by *
#Course
#GET course/description/filter/{courseID}
#Catalog
#GET course/catalog/filter/{subject}/{catalog}/{carreer}
test_file = "database.txt"
#End of variable declaration

#Step 1 CONCORDIA’S OPEN DATA api call ( api_call() )
def api_call():
	"""
	This function will make requests to Concordia's opendata api to get 
	string course dataset and string catalog dataset from opendata server.
	
	After receive both datasets, this function will merge both dataset and write 
	to local file "database.txt"
	:return:
	"""
	base_url="https://opendata.concordia.ca/API/v1/"
	raw_string_course=requests.get(base_url+"course/description/filter/*",auth=(User,Key)).content.decode()
	raw_string_catalog=requests.get(base_url+"course/catalog/filter/*/*/*",auth=(User,Key)).content.decode()
	
	raw_string_catalog=raw_string_catalog.replace("null","None")

	#list of course and catalog objects
	string_list_course = ast.literal_eval(raw_string_course)
	string_list_catalog = eval(raw_string_catalog)

	final_dictionary={}
	for i in copy.deepcopy(string_list_catalog):
		myid = i.pop('ID')
		final_dictionary[myid] = i

	for i in copy.deepcopy(string_list_course):
		key = i['ID']
		if key in final_dictionary:
			final_dictionary[key]['description'] = i['description']

	#The following code will parse the dictionary object
	# to remove all unecessary symbolss, then dump the dictionary object in local database file.
	with open(test_file,"w") as file:
		for key,item in final_dictionary.items():
			if "crosslisted" in item and item['crosslisted']==None:
				item['crosslisted']= "null"
			item['description']=item['description'].replace("\n"," ").replace("***","").replace("~~~","").replace("*KEYB*","").replace("<b>","").replace("\"","")
			item['description']=item['description'].replace("\\/","").replace("\r"," ").replace("\t"," ").replace("*VID*","").replace("*CNT*","").replace("NOTE:","NOTE ")
			item['title'] = item['title'].replace("\\/"," ").replace("\t"," ")
			item['prerequisites'] = item['prerequisites'].replace("\\/"," ").replace("\n"," ")
			item['sub_catalog'] = item['subject']+" "+item['catalog']
			file.write(json.dumps({key:item}))
			file.write("\n")
#End of api_call()

def parse_graduate_content(course_dict,miss_description_course_dict,soup,eng):
	"""
	This function will parse concordia graduate calendar webpage's content to
	retrive graduate class' description

	After getting a correct descrption for a graduate course, we will modify
	course_dict content

	:param course_dict: dict
	:param miss_description_course_dict: dict
	:param soup: BeautifulSoup
	:param eng: boolean
	:return:
	"""

	#engineering special note
	e02_note = "Subject matter will vary from term to term and from year to year. Students may re-register for these courses, providing that the course content has changed. Changes in content will be indicated by the letter following the course number, e.g., CIVI 691A, CIVI 691B, etc."
	all_span=soup.find_all("span",class_="large-text")
	for span in all_span:
		all_b_inspan = span.find_all("b")
		if span.string == None:
			span_str = str(span)
			span_b = str(span.b)
			for key,val in course_dict.items():
				if(len(val['sub_catalog'])==9 and not (val['sub_catalog'][-1].isdigit())):
					if( (val['subject'] in span_b and val['catalog'][:-1] in span_b) and "credit" in span_str and ("25 credits" not in span_str or "29 credits" not in span_str)):
						if "large-text" in max(span_str.split("\n"),key=len):
							if(eng):
								miss_description_course_dict[key]['description']=e02_note
							else:
								print("Found a class without description and its not in engineering")
						else:
							miss_description_course_dict[key]['description']=max(span_str.split("\n"),key=len).replace("<br/>","").replace("</span>","").replace("<b>Note:</b> ","")
				else:
					if( (val['subject'] in span_b and val['catalog'] in span_b) and "credit" in span_str and ("25 credits" not in span_str or "29 credits" not in span_str)):
						if "large-text" in max(span_str.split("\n"),key=len):
							if(eng):
								miss_description_course_dict[key]['description']=e02_note
							else:
								print("Found a class without description and its not in engineering")
						else:
							miss_description_course_dict[key]['description']=max(span_str.split("\n"),key=len).replace("<br/>","").replace("</span>","").replace("<b>Note:</b> ","")
							
		elif span.previous_sibling:
			for key,val in course_dict.items():
				if(len(val['sub_catalog'])==9 and not (val['sub_catalog'][-1].isdigit())):
					searching = str(span.previous_sibling.previous_sibling)
					if val['subject'] in searching and val['catalog'][:-1] in searching:
						if "<span class" not in str(span.string):
							miss_description_course_dict[key]['description']=span.string
				else:
					searching = str(span.previous_sibling.previous_sibling)
					if val['subject'] in searching and val['catalog'] in searching:
						if "<span class" not in str(span.string):
							miss_description_course_dict[key]['description']=span.string
#End of grad_scheme()

#Step 2 Crawling Concordia's undergraduate calendar
def undergrad_scheme():
	"""
	This function will crawl concordia's undergraduate calendar to get description
	for those classes that are missing description. After update, this function will
	update database and dump to local database file.

	This function used a speical library requests-futures for concurrent requests

	:return:
	"""

	base = "http://www.concordia.ca"
	url = "http://www.concordia.ca/academics/undergraduate/calendar/current/courses-quick-links.html"
	
	course_dict={}
	miss_description_course_dict={}

	#Build from local database file into two dictionaries
	with open(test_file,"r") as file:
		for line in file:
			obj=json.loads(line.replace("\n",""))
			course_dict[list(obj.keys())[0]]=obj[list(obj.keys())[0]]

	for key,val in course_dict.items():
		if "Calendar" in val['description']:
			miss_description_course_dict[key]=val


	#Requests concordia's undergraduate program page, to get course description from each subject
	request_result = requests.get(url)
	soup = BeautifulSoup(request_result.content,"lxml")

	all_a_links = soup.find_all("a",href=True)
	all_a_links_subject = []
	for a in all_a_links:
		if "/academics/undergraduate/calendar/current/sec" in a['href']:
			if "adhocenable" in a.attrs:
				all_a_links_subject.append(base+a['href'].split("#")[0])

	list_thread=[]
	list_content=[]
	all_a_links_subject = list(set(all_a_links_subject))

	#requests every subject's course description page
	with FuturesSession(max_workers=8,session=requests.Session()) as rq_session:
		for sub_url in all_a_links_subject:
			list_thread.append(rq_session.get(sub_url))

		for index,job in enumerate(as_completed(list_thread)):
			list_content.append(job.result().content)

	#parse all requests.content to find description
	for content in list_content:
		soup = BeautifulSoup(content,"lxml")
		all_b_tags = soup.find_all("b")
		for b_tag in all_b_tags:
			for key,val in miss_description_course_dict.items():
				if val['sub_catalog'] in str(b_tag):
					if b_tag.next_sibling and b_tag.next_sibling.next_sibling and b_tag.next_sibling.next_sibling.next_sibling:
						course_dict[key]['description']=str(b_tag.next_sibling.next_sibling.next_sibling)
						break

	with open(test_file,"w") as file:
		for key,val in course_dict.items():
			file.write(json.dumps({key:val}))
			file.write("\n")
#End of undergrad_scheme()

#Step 3 Crawling Concordia's graduate calendar
def graduate_scheme():
	"""
	This function will crawl concordia's graduate calendar to get description
	for those classes that are missing description. After update, this function will
	update database and dump to local database file.

	This function used a speical library requests-futures for concurrent requests

	:return:
	"""

	course_dict={}
	miss_description_course_dict={}
	with open(test_file,"r") as file:
		for line in file:
			obj=json.loads(line.replace("\n",""))
			course_dict[list(obj.keys())[0]]=obj[list(obj.keys())[0]]

	for key,val in course_dict.items():
		if "Calendar" in val['description']:
			miss_description_course_dict[key]=val

	base="https://www.concordia.ca"
	grad_program = "https://www.concordia.ca/admissions/graduate/programs.html"
	grad_calendar="/academics/graduate/calendar/current/"
	rq = requests.get(grad_program)
	soup = BeautifulSoup(rq.content,"lxml")
	all_a_links=soup.find_all("a",href=True)
	calendar_list=[]
	for a in all_a_links:
		if ("/academics/graduate/") in str(a):
			calendar_list.append(base+a['href'])

	list_thread=[]
	list_content=[]
	with FuturesSession(max_workers=8,session=requests.Session()) as rq_session:
		for sub_url in calendar_list:
			list_thread.append(rq_session.get(sub_url))

		for index,job in enumerate(as_completed(list_thread)):
			list_content.append(job.result().content)

	calendar_list=[]
	for content in list_content:
		soup = BeautifulSoup(content,"lxml")
		all_a = soup.find_all("a",adhocenable="false",href=True)
		for a in all_a:
			if "/academics/graduate/calendar" in a['href']:
				# print(a)
				calendar_list.append(base+a['href'].split("#")[0])

	calendar_list=list(set(calendar_list))
	list_thread=[]
	list_content=[]	
	with FuturesSession(max_workers=8,session=requests.Session()) as rq_session:
		for sub_url in calendar_list:
			list_thread.append(rq_session.get(sub_url))

		for index,job in enumerate(as_completed(list_thread)):
			list_content.append(job.result().content)

	for content in list_content:
		soup = BeautifulSoup(content,"lxml")
		h1 = soup.find_all("h1")
		for i in h1:
			if "Engineering Courses" in i:
				parse_graduate_content(miss_description_course_dict,course_dict,soup,True)
			else:
				parse_graduate_content(miss_description_course_dict,course_dict,soup,False)

	miss_description_course_dict={}
	for key,val in course_dict.items():
		if "Calendar" in val['description']:
			miss_description_course_dict[key]=val

	with open(test_file,"w") as file:
		for key,val in course_dict.items():
			file.write(json.dumps({key:val}))
			file.write("\n")
#End of graduate_scheme()

#Start of main 
if __name__ == '__main__':
	api_call()
	print("API CALL complete")
	print("Building undergrade scheme [...]")
	undergrad_scheme()
	print("Undergrade scheme built")
	print("Building graduate scheme [...]")
	graduate_scheme()
	print("Graduate scheme built")
	print("Database complete")