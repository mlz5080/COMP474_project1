#COMP 474 LAB 9

##################### TASK 1 ##################### 
import aiml_bot
bot = aiml_bot.Bot(learn="mybot.aiml")

while True:
    print(bot.respond(input("> ")))
##################### END OF TASK 1 ##################### 

##################### TASK 2 ##################### 
# import numpy as np
# from sklearn.neighbors import KNeighborsClassifier
# from sklearn.feature_extraction.text import TfidfVectorizer

# corpus = np.array([
#         'Who is Bill Gates',
#         'Where is Concordia located',
#         'What is AI',
#         'What is Sean2',
#         'What city is McGill located in',
#         'Who is McGill'
# ])

# vectorizer = TfidfVectorizer()
# X = vectorizer.fit_transform(corpus)

# # Encode labels: 0="Person", 1="Location", 2="Definition"
# y = np.array([0,1,2,2,1,0])

# clf = KNeighborsClassifier(3)
# clf.fit(X, y)

# q = 'What is Naes1'
# q_vec = vectorizer.transform([q])
# predict = clf.predict(q_vec)
# print('Predicted class = ', predict)
##################### END OF TASK 2