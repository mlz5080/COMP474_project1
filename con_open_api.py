import requests,ast
from requests_futures.sessions import FuturesSession
from concurrent.futures import as_completed
import json
import copy
from bs4 import BeautifulSoup
import re

User="124"
Key="d3c1c8924a8d59f9b5f29f54bbbbb5e7"

	#API format
	#Any parameter could be replaced by *
	#Course
	#GET course/description/filter/{courseID}
	#Catalog
	#GET course/catalog/filter/{subject}/{catalog}/{carreer}
def api_call():
	base_url="https://opendata.concordia.ca/API/v1/"
	raw_string_course=requests.get(base_url+"course/description/filter/*",auth=(User,Key)).content.decode()
	raw_string_catalog=requests.get(base_url+"course/catalog/filter/*/*/*",auth=(User,Key)).content.decode()
	
	raw_string_catalog=raw_string_catalog.replace("null","None")

	#dicionary of course and catalog
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

	print(final_dictionary)

	# print(string_list_catalog)
	# print(string_list_course)
	print(len(string_list_course),len(string_list_catalog))

	with open("final_copy.txt","w") as file:
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
#api_call()



#writetofile()


# content=[]
# list_thread=[]
# list_response=[]

#dead end, try to see why course set has more ID than catalog set.
def multiple_requests():
	mylist = {}
	e02_note = "Subject matter will vary from term to term and from year to year. Students may re-register for these courses, providing that the course content has changed. Changes in content will be indicated by the letter following the course number, e.g., CIVI 691A, CIVI 691B, etc."
	"""
	url = ["https://www.concordia.ca/jmsb/programs/undergraduate/bachelor/majors/business-technology-management/courses.html",
	"https://www.concordia.ca/jmsb/programs/undergraduate/bachelor/majors/accountancy/courses.html",
	"https://www.concordia.ca/jmsb/programs/undergraduate/bachelor/program-structure/core-courses.html",
	"https://www.concordia.ca/jmsb/programs/undergraduate/bachelor/majors/finance/courses.html",
	"https://www.concordia.ca/jmsb/programs/undergraduate/bachelor/majors/human-resource-management/courses.html",
	"https://www.concordia.ca/jmsb/programs/undergraduate/bachelor/majors/international-business/courses.html",
	"https://www.concordia.ca/jmsb/programs/undergraduate/bachelor/majors/management/courses.html",
	"https://www.concordia.ca/jmsb/programs/undergraduate/bachelor/majors/marketing/courses.html",
	"https://www.concordia.ca/jmsb/programs/undergraduate/bachelor/majors/supply-chain-operations-management/courses.html"
	]
	"""

	#url_FA_SC_ud="http://www.concordia.ca/academics/undergraduate/calendar/current/sec31/31.html"

	#url_eng_grad="http://www.concordia.ca/academics/graduate/calendar/current/encs/engineering-courses.html"
	
	base="http://www.concordia.ca"
	url ="http://www.concordia.ca/academics/graduate/calendar/current/jmsb.html"

	with open("final_copy.txt","r") as file:
		for line in file:
			#print(line)
			obj=json.loads(line.replace("\n",""))
			mylist[list(obj.keys())[0]]=obj[list(obj.keys())[0]]

	courselist = {}
	for key,val in mylist.items():
		if( "Calendar" in val['description']):
			courselist[key]=val
			print(val['sub_catalog'],val['description'])
	# print(len(courselist))

	# return
	list_url=[]

	soup = BeautifulSoup(requests.get(url).content,"lxml")
	############ Retrive from Master program main page ############# 
	all_a = soup.find_all("a",adhocenable="false",href=True)
	for a in all_a:
		if("MBA" in str(a) or "PhD" in str(a) or "Diploma" in str(a) or 
			"MSc" in str(a) or "MSCM" in str(a) or "MIM" in str(a)
			or "MApCompSc" in str(a) or "Certificate" in str(a) or
			"MASc" in str(a) or "MEng" in str(a)):
			print(a)
			list_url.append(base+str(a['href']))

	# for i in courselist:
	# 	print(i[1]['sub_catalog'])

	list_thread=[]
	list_response=[]

	with FuturesSession(max_workers=8,session=requests.Session()) as rq_session:
		for sub_url in list_url:
			list_thread.append(rq_session.get(sub_url))

		for index,job in enumerate(as_completed(list_thread)):
			list_response.append(job.result())

		for response in list_response:

##################################################################		
			#rp = requests.get("http://www.concordia.ca/academics/graduate/calendar/current/encs/computer-science-courses.html")
			soup = BeautifulSoup(response.content,"lxml")
			all_span=soup.find_all("span",class_="large-text")
			for span in all_span:
				all_b_inspan = span.find_all("b")
				if span.string == None:
					span_str = str(span)
					span_b = str(span.b)
					for key,val in courselist.items():
						if(len(val['sub_catalog'])==9 and not (val['sub_catalog'][-1].isdigit())):
							if( (val['subject'] in span_b and val['catalog'][:-1] in span_b) and "credit" in span_str and ("25 credits" not in span_str or "29 credits" not in span_str)):
								#print("\nDo not have string")
								# if "large-text" in max(span_str.split("\n"),key=len):
								# 	mylist[key]['description']=e02_note
								# else:
								print(val['sub_catalog'])
								mylist[key]['description']=max(span_str.split("\n"),key=len).replace("<br/>","").replace("</span>","").replace("<b>Note:</b> ","")

						else:
							if( (val['subject'] in span_b and val['catalog'] in span_b) and "credit" in span_str and ("25 credits" not in span_str or "29 credits" not in span_str)):
								#print("\nDo not have string")
								print(val['sub_catalog'])
								mylist[key]['description']=max(span_str.split("\n"),key=len).replace("<br/>","").replace("</span>","").replace("<b>Note:</b> ","")
				elif span.previous_sibling:
					for key,val in courselist.items():
						if(len(val['sub_catalog'])==9 and not (val['sub_catalog'][-1].isdigit())):
							searching = str(span.previous_sibling.previous_sibling)
							if val['subject'] in searching and val['catalog'][:-1] in searching:
								print(val['sub_catalog'])
								mylist[key]['description']=span.string
						else:
							searching = str(span.previous_sibling.previous_sibling)
							if val['subject'] in searching and val['catalog'] in searching:
								print(val['sub_catalog'])
								mylist[key]['description']=span.string
	# 	#print(mylist)
##################################################################	
	courselist = {}
	for key,val in mylist.items():
		if( "Calendar" in val['description']):
			courselist[key]=val
	print(len(courselist))

	with open("final_copy_2.txt","w") as file:
		for key,val in mylist.items():
			file.write(json.dumps({key:val}))
			file.write("\n")






	# for i in soup.find_all("b"):
	# 	b_str=str(i)
	# 	for key,val in courselist.items():
	# 		if "AHSC" in val['sub_catalog']:
	# 			print(val['sub_catalog'])
		#print(all_span)


def grad_eng_schema():
	#e02_note = "Subject matter will vary from term to term and from year to year. Students may re-register for these courses, providing that the course content has changed. Changes in content will be indicated by the letter following the course number, e.g., CIVI 691A, CIVI 691B, etc."
	for span in all_span:
		all_b_inspan = span.find_all("b")
		if span.string == None:
			span_str = str(span)
			span_b = str(span.b)
			for key,val in courselist.items():
				if(val['sub_catalog'] in span_b and "credit" in span_str and ("25 credits" not in span_str or "29 credits" not in span_str)):
					#print("\nDo not have string")
					if "large-text" in max(span_str.split("\n"),key=len):
						mylist[key]['description']=e02_note
						#print(e02_note)
					else:
						#print(max(span_str.split("\n"),key=len).replace("<br/>","").replace("</span>","").replace("<b>Note:</b> ",""))
						mylist[key]['description']=max(span_str.split("\n"),key=len).replace("<br/>","").replace("</span>","").replace("<b>Note:</b> ","")
		elif span.previous_sibling:
			for key,val in courselist.items():
				if val['sub_catalog'] in str(span.previous_sibling.previous_sibling):
					mylist[key]['description']=span.string
					#print("\nHas string")
					#print(span.string)
	#print(mylist)
	# with open("final_copy_2.txt","w") as file:
	# 	for key,val in mylist.items():
	# 		file.write(json.dumps({key:val}))
	# 		file.write("\n")
	

	# 	for i in url:
	# 		list_thread.append(rq_session.get(i))
	# 	for i in list_thread:
	# 		list_response.append(i.result())

def jmsb_schema():
	#pass
	# UGRAD JMSB schema
	mylist={}
	with open("final_copy.txt","r") as file:
		for line in file:
			#print(line)
			obj=json.loads(line.replace("\n",""))
			mylist[list(obj.keys())[0]]=obj[list(obj.keys())[0]]

	courselist = {}
	for key,val in mylist.items():
		if( "Calendar" in val['description']):
			courselist[key]=val

	url = "https://www.concordia.ca/jmsb/programs/graduate/cpa/program-details/curriculum.html"
	response=requests.get(url)
	soup = BeautifulSoup(response.content,"lxml")
	all_course_div = soup.find_all("div",class_="course-description list parbase section")
	for div in all_course_div:
		suba = div.find_all("a",attrs={"name":"legend-expand"})
		for a in suba:
			for key,val in courselist.items():
				if a.find(string=re.compile(val['sub_catalog'])):
					description_div = div.find("div",class_="rte span12")
					description = description_div.find_all("p")
					mylist[key]['description']=str(description[0]).replace("<p>","").replace("</p>","")

	courselist = {}
	for key,val in mylist.items():
		if( "Calendar" in val['description']):
			courselist[key]=val
	print(len(courselist))

	with open("final_copy_2.txt","w") as file:
		for key,val in mylist.items():
			file.write(json.dumps({key:val}))
			file.write("\n")

	# 	for i in list_response:
	# 		#print(resposne)
	# 		

	# courselist = []
	# print(len(mylist))
	# for data in mylist:
	# 	for key,val in data.items():
	# 		if( "Calendar" in val['description']):
	# 			courselist.append([key,val])
	# print(len(courselist))

	# with open("final_copy.txt","w") as file:
	# 	for obj in mylist:
	# 		file.write(json.dumps(obj))
	# 		file.write("\n")
		
		#print(all_b_tags)

		# for i in courselist:
		# 	for link in all_b_tags:
		# 		#print(i)
		# 		#print(link)
		# 		if link.find(string=re.compile(i)):
		# 			print(i)
		# 			print(link.next_sibling.next_sibling.next_sibling)
		# 			# for i in link.children:
		# 			# 	print(i)

		# 			break

#multiple_requests()
jmsb_schema()





