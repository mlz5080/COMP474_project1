import json
from rdflib import *
from rdflib.namespace import *
from rdflib.util import *

dbp = Namespace("http://dbpedia.org/resource/")



g = Graph()


nsm = NamespaceManager(g)
nsm.bind('dbr', 'http://dbpedia.org/resource/')
nsm.bind('ex', 'http://example.org/')
nsm.bind('focu', 'http://focu.io/schema#')

temp = '{"000027": {"title": "Introduction to Financial Accounting", "subject": "ACCO", "catalog": "230", "career": "UGRD", "classUnit": "3.00", "prerequisites": "   Never Taken Not Registered: ACCO213, ACCO220, COMM217; Never Taken: ACCO240, ACCO340, ACCO345, ACCO365, ACCO455, ACCO470F, ACCO470I, ACCO470S, ACCO470T, COMM305, COMM308, IBUS471I", "crosslisted": null, "description": "This course provides an introduction to accounting concepts underlying financial statements of organizations. It focuses on the analysis, measurement, and reporting of business transactions to users of financial statements. It also examines the uses and limitations of accounting information for investment and credit decisions.  NOTE  JMSB students may not take this course for credit. NOTE  Students who receive a grade of C or better may be exempt from COMM 217. NOTE  Students who have received credit for ACCO 220 may not take this course for credit.  "}}'
temp = json.loads(temp)

# COURSE
title_id = list(temp.keys())[0] 
title = temp[title_id]['title'] # Title (String)
subject = temp[title_id]['subject'] # Subject (String)
catalog = temp[title_id]['catalog'] # Catalog (int)
career = temp[title_id]['career'] # Career (String)
description = temp[title_id]['description'] # Description (String)

# TOPICS
# Title + Description
topics = title + "," + description


# print(title)
# print(subject)
# print(catalog)
# print(career)
# print(description)
# print(topics)
#
subject_catalog = from_n3('ex:' + subject + catalog, nsm=nsm)

g.add((subject_catalog, RDF.type, from_n3('dbr:Course_(education)', nsm=nsm)))
g.add((subject_catalog, RDFS.label, Literal(title)))
g.add((subject_catalog, from_n3('focu:subject', nsm=nsm), Literal(subject)))
g.add((subject_catalog, from_n3('focu:catalog', nsm=nsm), Literal(catalog)))
g.add((subject_catalog, RDFS.comment, Literal(description)))


for s, p, o in g:
	print (s, p, o)







