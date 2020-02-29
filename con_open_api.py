import requests,ast
from requests_futures.sessions import FuturesSession
from concurrent.futures import as_completed
import json
import copy

User="124"
Key="d3c1c8924a8d59f9b5f29f54bbbbb5e7"

#API format
#Any parameter could be replaced by *
#Course
#GET course/description/filter/{courseID}
#Catalog
#GET course/catalog/filter/{subject}/{catalog}/{carreer}

base_url="https://opendata.concordia.ca/API/v1/"
raw_string_course=requests.get(base_url+"course/description/filter/*",auth=(User,Key)).content.decode()
raw_string_catalog=requests.get(base_url+"course/catalog/filter/*/*/*",auth=(User,Key)).content.decode()
raw_string_catalog=raw_string_catalog.replace("null","None")
#print(raw_string_catalog)


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

# course_set=set([i["ID"] for i in string_list_course])
# catalog_set=set([i["ID"] for i in string_list_catalog])
# difference = course_set-catalog_set
def writetofile():
	with open("course.txt","w") as file:
		for i in string_list_course:
			i['description']=i['description'].replace("\n"," ").replace("***","").replace("~~~","").replace("*KEYB*","").replace("<b>","")
			i['description']=i['description'].replace("\\/","").replace("\r"," ").replace("\t"," ").replace("*VID*","").replace("*CNT*","")
			file.write(json.dumps(i))
			file.write("\n")

	with open("catalog.txt","w") as file:
		for i in string_list_catalog:
			i['title'] = i['title'].replace("\\/"," ").replace("\t"," ")
			i['prerequisites'] = i['prerequisites'].replace("\\/"," ").replace("\n"," ")
			file.write(json.dumps(i))
			file.write("\n")

	with open("final_copy.txt","w") as file:
		for key,item in final_dictionary.items():
			item['description']=item['description'].replace("\n"," ").replace("***","").replace("~~~","").replace("*KEYB*","").replace("<b>","").replace("\"","")
			item['description']=item['description'].replace("\\/","").replace("\r"," ").replace("\t"," ").replace("*VID*","").replace("*CNT*","").replace("NOTE:","NOTE ")
			item['title'] = item['title'].replace("\\/"," ").replace("\t"," ")
			item['prerequisites'] = item['prerequisites'].replace("\\/"," ").replace("\n"," ")
			file.write(json.dumps({key:item}))
			file.write("\n")

writetofile()

# with open("difference.txt","w") as file:
# for i in difference:
# 	file.write(i)
# 	file.write("\n")

# course_set=set([i["ID"] for i in string_list_course])
# catalog_set=set([i["ID"] for i in string_list_catalog])
# print(len(course_set),len(catalog_set))

content=[]
list_thread=[]
list_response=[]



#dead end, try to see why course set has more ID than catalog set.
def multiple_requests():
	with FuturesSession(max_workers=8,session=requests.Session()) as rq_session:
		for cid in course_set-catalog_set:
			list_thread.append(rq_session.get(base_url+"course/description/filter/"+cid,auth=(User,Key)))

		for index,job in enumerate(as_completed(list_thread)):
			list_response.append(job.result())

		for response in list_response:
			print(response.content.decode())