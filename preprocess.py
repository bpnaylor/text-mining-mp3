import time
import os
import sys
import json
import codecs
import re
import math
from nltk.tokenize import wordpunct_tokenize as tokenize
from nltk.stem.snowball import SnowballStemmer
stemmer = SnowballStemmer("english")

import pprint as pp

if sys.stdout.encoding != 'UTF-8':
	sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
if sys.stderr.encoding != 'UTF-8':
	sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

def main():
	start_time = time.time()

	all_files = []
	data_path = os.path.abspath(sys.argv[1])
	stopwords_path = os.path.abspath(sys.argv[2])

	load_stopwords(stopwords_path)
	file_names = load_directory(data_path)
	load_restaurants(file_names)

	for restaurant in m_restaurants:
		preprocess_reviews(restaurant)

	for restaurant in m_restaurants:
		for review in restaurant["Reviews"]:
			smooth(review)

	with open('train.txt','w',encoding="utf-8") as outfile:
		json.dump(m_restaurants, outfile, ensure_ascii=False)

	# with open('vocab.txt', 'w', encoding="utf-8") as vocabfile:
	# 	json.dump(m_vocab, vocabfile, ensure_ascii=False)

	print("Time: " + str(time.time() - start_time))

def load_stopwords(path):
	global m_stopwords
	file = open(path, "r", encoding="utf-8")
	s = file.read().split("\n\n")

	for stopword in s:
		m_stopwords[stemmer.stem(normalize(stopword))] = 0

	file.close()

def load_directory(path):
	f = []
	for root, dirs, files in os.walk(path, topdown=False):
		for name in files:
			f.append(os.path.join(root, name))
		for name in dirs:
			load_directory(os.path.join(root, name))
	return(f)

def load_restaurants(files):
	for f in files:
		file = open(f, 'r', encoding='utf-8')
		restaurant = json.load(file)
		m_restaurants.append(restaurant)
		file.close()

def preprocess_reviews(restaurant):
	global m_numreviews

	for review in restaurant["Reviews"]:
		content = review["Content"]
		vocab = {}

		tokens = tokenize(content)
		temp = []

		for t in tokens:
			token = stemmer.stem(normalize(t))
			if token not in m_stopwords and token:
				temp.append(token)
				check_dict(vocab, token)
				check_dict(m_vocab, token)

		review["Content"] = temp
		review["Vector"] = vocab
		m_numreviews += 1

def check_dict(dictionary, key):
	if key in dictionary:
		dictionary[key] += 1
	else:
		dictionary[key] = 1

def smooth(review):
	to_delete = {}
	for word in review["Vector"]:
		if m_vocab[word] > 10:
			tf = 1 + math.log(review["Vector"][word])
			idf = m_numreviews / m_vocab[word]
			review["Vector"][word] = tf*idf
		else:
			to_delete[word] = 0

	for d in to_delete:
		del review["Vector"][d]

def normalize(token):
	token = re.sub(r"\W+","", token)
	token = re.sub(r"\d+","NUM", token)
	token = re.sub(r"([,.'\"-\/:!?)()])", "", token)
	return(token)

# global variables
m_restaurants = []
m_stopwords = {}
m_vocab = {}
global m_numreviews
m_numreviews = 0

main()
