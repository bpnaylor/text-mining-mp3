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
	start_time = time.time()

	data_path = os.path.abspath(sys.argv[1])
	controlled_dict_path = os.path.abspath(sys.argv[2])
	output_path = os.path.abspath(sys.argv[3])
	query_path = os.path.abspath(sys.argv[4])

	load_data(data_path)
	load_controlled_dict(controlled_dict_path)
	load_query(query_path)

	l = 5
	generate_l_vectors(l)
	random_projection(l)

	with open(output_path,'w',encoding="utf-8") as outfile:
		json.dump(m_restaurants, outfile, ensure_ascii=False)

	with open("hashedquery.json",'w',encoding="utf-8") as outfile2:
		json.dump(m_query, outfile2, ensure_ascii=False)

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

# generate random matrix with np.shape(matrix) = (l_bits, m), values in [-1,1]
def generate_l_vectors(l_bits):
	global m

	for i in range(l_bits):
		l_vectors.append([])
		
		for j in range(m):
			l_vectors[i].append(random.uniform(-1,1))

# hash all reviews
def random_projection(l_bits):
	for restaurant in m_restaurants:
		for review in restaurant["Reviews"]:
			hash_review(review, l_bits)

	for review in m_query["Reviews"]:
		hash_review(review, l_bits)

# hash(5000-feature vector) -> l-bit binary vector
def hash_review(review, l_bits):
	h = []
	x = get_vector(review)

	for i in range(l_bits):
		h.append(sgn(np.dot(l_vectors[i], x)))

	review["Hash"] = h

def sgn(value):
	if value>=0:
		return(1)
	else:
		return(0)

# create full-dimensional vectors on the fly to save memory
def get_vector(review):
	v = []
	for t in controlled_dict:
		if t in review["Vector"]:
			v.append(review["Vector"][t])
		else:
			v.append(0.0)
	return(v)

controlled_dict = {}
m_restaurants = []
l_vectors = []
m_query = []

global m

main()