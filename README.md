# COMP474_project1
Concordia graph

The following discribes which file(s) belong to which deliverable.

### DELIVERABLES ###

# RDF Schema;
schema.ttl

# Dataset;
database.txt

# Knowledge Base Construction;
database_builder.py - Please use the following command to install python's dependencies.
>pip install rdflib
>pip install requests
>pip install requests-futures

# Knowledge Base;
parse.py - Builds the Knowledge Graph with docker image of DBpedia Spotlight running locally. Use the following command to RUN DOCKER LOCALLY
>sudo docker run -i -p 2222:80 dbpedia/spotlight-english spotlight.sh

query.py - Allows a user to query Knowledge Graph with questions from Assignment description

# Queries and their results;
Queries; found in [path-to-project]/COMP474_project1/queries directory

Results; found in the [path-to-project]COMP474_project1/results directory


