import time
import os
import sys
import json
import codecs
import math

if sys.stdout.encoding != 'UTF-8':
	sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
if sys.stderr.encoding != 'UTF-8':
	sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

def main():
	start_time = time.time()

	data_path = os.path.abspath(sys.argv[1])
	load_data(data_path)
	count()
	extract_features()
	# get_top_features(num_features)

	# print("Time: " + str(time.time() - start_time))

def load_data(path):
	data = open(path, 'r', encoding='utf-8')
	global m_restaurants
	m_restaurants = json.load(data)
	data.close()

def count():
	global num_positive
	global num_negative

	for i in range(len(m_restaurants)):
		for review in m_restaurants[i]["Reviews"]:
			if float(review["Overall"]) < 4.0:
				num_negative += 1
			else:
				num_positive += 1

			for term in review["Vector"]:
				check_dict(vocab, term)

				if float(review["Overall"]) < 4.0:
					check_dict(c, term)
				else:
					check_dict(a, term)

def extract_features():
	for i in range(len(m_restaurants)):
		for review in m_restaurants[i]["Reviews"]:
			for term in review["Vector"]:
				chi_square(term)
				IG(term)

def get_features():
	# get words only
	cs_sorted = [t for t in sorted(cs, key=cs.get, reverse=True)]
	ig_sorted = [t for t in sorted(ig, key=ig.get, reverse=True)]
	ig_sorted = ig_sorted[:5000]

	# # check: no new words contributed by chi-square set?
	# for a in cs_sorted:
	# 	if a not in ig_sorted:
	# 		print("Unique to Chi-Square: ", a)

	# union of both sets of features
	features = list(set(cs_sorted) | set(ig_sorted))

	# export vocabulary list
	for i in range(len(features)):
		print(features[i])

def get_top_features(num_features):
	# get words and 
	cs_sorted = [(t, cs[t]) for t in sorted(cs, key=cs.get, reverse=True)]
	ig_sorted = [(t, ig[t]) for t in sorted(ig, key=ig.get, reverse=True)]
	ig_sorted = ig_sorted[:5000]

	print("Top features by chi-square:")
	for i in range(num_features):
		print(cs_sorted[i][0],cs_sorted[i][1])

	print("")

	print("Top features by information gain:")
	for i in range(num_features):
		print(ig_sorted[i][0],ig_sorted[i][1])


def chi_square(term):
	bb = checkB(term)
	dd = checkD(term)
	aa = a[term]
	cc = c[term]

	chisq = aa + bb + cc + dd
	chisq = chisq * math.pow(aa*dd-bb*cc,2)
	chisq = chisq / ((aa+cc)*(bb+dd)*(aa+bb)*(cc+dd))
	
	if chisq >= 3.841:
		cs[term] = chisq

def checkB(term):
	global num_positive

	if term not in b:
		if term in a:
			b[term] = num_positive - a[term]
		else:
			a[term] = 0
			b[term] = num_positive
	return(b[term])

def checkD(term):
	global num_negative

	if term not in d:
		if term in c:
			d[term] = num_negative - c[term]
		else:
			c[term] = 0
			d[term] = num_negative
	return(d[term])

def IG(term):
	global num_positive
	global num_negative

	num_documents = num_positive + num_negative

	g = - entropy(p("y=0","")) - entropy(p("y=1",""))
	g += p("t",term)*entropy(p("y=0|t",term))	
	g += p("t",term)*entropy(p("y=1|t",term))
	g += p("~t",term)*entropy(p("y=0|~t",term))
	g += p("~t",term)*entropy(p("y=1|~t",term))
	ig[term] = g

def entropy(prob):
	return(prob*log(prob))

def check_dict(dictionary, key):
	if key in dictionary:
		dictionary[key] += 1
	else:
		dictionary[key] = 1

def log(prob):
	if prob <= 0.0:
		return(0.0)
	else:
		return(math.log(prob))

# hahaha
def p(which, term):
	global num_negative
	global num_positive

	num_documents = num_positive + num_negative

	if which == "y=0":
		return(num_negative/num_documents)
	if which == "y=1":
		return(num_positive/num_documents)
	if which == "t":
		return(vocab[term] / num_documents)
	if which == "~t":
		return((num_documents - vocab[term]) / num_documents)
	if which == "y=0|t":
		return(c[term] / vocab[term])
	if which == "y=1|t":
		return(a[term] / vocab[term])
	if which == "y=0|~t":
		return(b[term] / (num_documents - vocab[term]))
	if which == "y=1|~t":
		return(d[term] / (num_documents - vocab[term]))
	else:
		sys.exit("you fucked up")

a = {}
b = {}
c = {}
d = {}
cs = {}
ig = {}
vocab = {}
doc = {}
features = {}

global num_positive
num_positive = 0
global num_negative
num_negative = 0
main()