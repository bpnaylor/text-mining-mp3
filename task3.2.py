import time
import os
import sys
import json
import codecs
import math
import numpy as np
import random

if sys.stdout.encoding != 'UTF-8':
	sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
if sys.stderr.encoding != 'UTF-8':
	sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

def main():
	data_path = os.path.abspath(sys.argv[1])
	controlled_dict_path = os.path.abspath(sys.argv[2])
	query_path = os.path.abspath(sys.argv[3])

	load_data(data_path)
	load_controlled_dict(controlled_dict_path)
	load_query(query_path)
	to_list()

	start_time = time.time()
	k = 5
	knn_query(k)

	print("Time: " + str(time.time() - start_time))

def load_data(path):
	data = open(path, 'r', encoding='utf-8')
	global m_restaurants
	m_restaurants = json.load(data)
	data.close()

def load_controlled_dict(path):
	global controlled_dict
	global m

	file = open(path, "r", encoding="utf-8")
	cd = file.read().split("\n")

	for word in cd:
		controlled_dict[word] = 0

	m = len(controlled_dict)

	file.close()

def load_query(path):
	file = open(path,'r',encoding='utf-8')
	global m_query
	m_query = json.load(file)
	file.close()

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

def knn(k, query):
	h_q = query["Hash"]
	v_q = get_vector(query)

	distances = []
	neighbours = []

	for i in range(len(m_restaurants)):
		reviews = m_restaurants[i]["Reviews"]
		for j in range(len(reviews)):
			review = reviews[j]
			h_r = review["Hash"]

			# if h_r == h_q:
			v_r = get_vector(review)
			distance = get_cosine_similarity(v_r,v_q)
			distances.append([distance,i,j])

	distances.sort(reverse=True)

	for i in range(k):
		d = distances[i][0]
		x = distances[i][1]
		y = distances[i][2]
		neighbours.append([d, m_restaurants[x]["Reviews"][y]])

	return(neighbours)

def knn_query(k):
	for review in m_query["Reviews"]:
		print("Querying", review["ReviewID"])
		neighbours = knn(k,review)

		print(review["Content"])

		for i in range(k):
			print(neighbours[i][0])
			print(neighbours[i][1]["Content"])

controlled_dict = {}
m_restaurants = []
l_vectors = []
m_query = []
global m

main()