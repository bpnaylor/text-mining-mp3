import time
import os
import sys
import json
import codecs
import math
import numpy as np
from sklearn.metrics import precision_recall_fscore_support
from sklearn.model_selection import KFold

import matplotlib.pyplot as plt

if sys.stdout.encoding != 'UTF-8':
	sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
if sys.stderr.encoding != 'UTF-8':
	sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

def main():
	global start_time
	start_time = time.time()

	data_path = os.path.abspath(sys.argv[1])
	controlled_dict_path = os.path.abspath(sys.argv[2])

	restaurants = load_data(data_path)
	load_controlled_dict(controlled_dict_path)
	to_list()

	split_data(restaurants)

	print("Time: " + str(time.time() - start_time))

def load_data(path):
	file = open(path, 'r', encoding='utf-8')
	data = json.load(file)
	file.close()
	return(data)

def load_controlled_dict(path):
	global controlled_dict
	file = open(path, "r", encoding="utf-8")
	cd = file.read().split("\n")

	for word in cd:
		controlled_dict[word] = 0

	file.close()

def split_data(restaurants):

	global start_time

	# nb_precisions = []
	# nb_recalls = []
	# nb_fscores = []

	knn_precisions = []
	knn_recalls = []
	knn_fscores = []

	# flatten restaurants object
	all_restaurants = []
	for i in range(len(restaurants)):
		for j in range(len(restaurants[i]["Reviews"])):
			all_restaurants.append([restaurants[i]["RestaurantInfo"],restaurants[i]["Reviews"][j]])

	kf = KFold(n_splits=10, shuffle=True, random_state=0)

	for train_indices, test_indices in kf.split(all_restaurants):

		print("Time: " + str(time.time() - start_time))		

		train_reviews = []
		test_reviews = []

		for i in train_indices:
			review = all_restaurants[i][1]
			# count(review)
			train_reviews.append(review)

		for i in test_indices:
			test_reviews.append(all_restaurants[i][1])
		
		true_classes, est_classes = knn(5, test_reviews, train_reviews)
		metrics = precision_recall_fscore_support(true_classes, est_classes, average="weighted", beta=1.0)

		knn_precisions.append(metrics[0])
		knn_recalls.append(metrics[1])
		knn_fscores.append(metrics[2])

		# true_classes, est_classes = naive_bayes(test_reviews)
		# metrics = precision_recall_fscore_support(true_classes, est_classes, average="weighted", beta=1.0)

		# nb_precisions.append(metrics[0])
		# nb_recalls.append(metrics[1])
		# nb_fscores.append(metrics[2])
		
		# # reset for next round of nb
		# global num_neg_docs
		# global num_pos_docs

		# num_neg_docs = 0
		# num_pos_docs = 0

		# total_vocab.clear()
		# neg_vocab.clear()
		# pos_vocab.clear()

	# print("Naive Bayes.")
	# print("Average precision:", nb_precisions)
	# print("Average recall:", nb_recalls)
	# print("Average F1-score:", nb_fscores)

	print("KNN.")
	print("Average precision:", knn_precisions)
	print("Average recall:", knn_recalls)
	print("Average F1-score:", knn_fscores)

def count(review):
	global num_neg_docs
	global num_pos_docs

	if float(review["Overall"]) < 4.0:
		num_neg_docs += 1
		for term in review["Content"]:
			check_dictionary(total_vocab, term)
			if term in controlled_dict:
				check_dictionary(neg_vocab, term)
	else:
		num_pos_docs += 1
		for term in review["Content"]:
			check_dictionary(total_vocab, term)
			if term in controlled_dict:
				check_dictionary(pos_vocab, term)

# naive bayes classifier

def naive_bayes(reviews):
	true_classes = []
	est_classes = []
	decision_functions = []

	for review in reviews:
		if float(review["Overall"]) < 4.0:
			true_classes.append(0)
		else:
			true_classes.append(1)

		est_class = linear(review)
		est_classes.append(est_class)

	return(true_classes, est_classes)

def linear(review):
	f_x = math.log(p("y=1","")/p("y=0",""))

	for x in review["Content"]:
		f_x += math.log(p("w|y=1",x)) - math.log(p("w|y=0",x))

	return(sgn(f_x))

def sgn(f):
	if f>=0:
		return(1)
	else:
		return(0)

def p(which, term):
	if which == "w|y=0":
		return(smooth(neg_vocab, term))
	if which == "w|y=1":
		return(smooth(pos_vocab, term))
	if which == "y=1":
		return(num_pos_docs/(num_pos_docs+num_neg_docs))
	if which == "y=0":
		return(num_neg_docs/(num_pos_docs+num_neg_docs))
	else:
		system.exit("you fucked up")

def smooth(dictionary, w):
	delta = 0.1
	if w in dictionary:
		return((dictionary[w] + delta)/(2+delta*(len(total_vocab))))
	else:
		return(delta/(2+delta*(len(total_vocab))))

def check_dictionary(dictionary, key):
	if key in dictionary:
		dictionary[key] += 1
	else:
		dictionary[key] = 1

# kNN classifier

def to_list():
	i = 0
	for t in controlled_dict:
		controlled_dict[t] = i
		i+=1

# create full-dimensional vectors on the fly to save memory
def get_vector(review):
	v = np.zeros((5000))
	for t in review["Vector"]:
		if t in controlled_dict:
			v[controlled_dict[t]] = review["Vector"][t]
	return(v)

def get_cosine_similarity(vector_i, vector_j):
	if len(vector_i) != len(vector_j):
		sys.exit("Error in reviews", review_i["ReviewID"], "and", review_j["ReviewID"], ":", len(v_i), "vs", len(v_j))
	
	norm_i = np.linalg.norm(vector_i)
	norm_j = np.linalg.norm(vector_j)

	return(np.dot(vector_i,vector_j)/(norm_i*norm_j))

def knn_query(k, query, reviews):
	h_q = query["Hash"]
	v_q = get_vector(query)
	num_matches = 0

	distances = []
	neighbours = []

	for j in range(len(reviews)):
		h_r = reviews[j]["Hash"]

		if h_r == h_q:
			num_matches += 1
			v_r = get_vector(reviews[j])
			distance = get_cosine_similarity(v_r,v_q)
			distances.append([distance,j])

	if num_matches == 0:
		print("Problem query:",query["ReviewID"])

	distances.sort(reverse=True)

	for i in range(k):
		d = distances[i][0]
		ind = distances[i][1]
		neighbours.append([d,reviews[ind]])

	return(neighbours)

def knn(k, test, train):
	true_classes = []
	est_classes = []

	for review in test:
		if float(review["Overall"]) < 4.0:
			true_classes.append(0)
		else:
			true_classes.append(1)

		neighbours = knn_query(k,review,train)

		pos = 0
		neg = 0
		for i in range(k):
			if float(neighbours[i][1]["Overall"]) > 4.0:
				pos+=1
			else:
				neg+=1

		if pos > neg:
			est_classes.append(1)
		else:
			est_classes.append(0)

	return(true_classes,est_classes)

# global variables

total_vocab = {}
pos_vocab = {}
neg_vocab = {}
controlled_dict = {}
controlled_list = []
all_restaurants = []

global num_pos_docs
num_pos_docs = 0
global num_neg_docs
num_neg_docs = 0

global start_time

main()
