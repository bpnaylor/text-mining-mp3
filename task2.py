import time
import os
import sys
import json
import codecs
import math

from sklearn.metrics import average_precision_score
from sklearn.metrics import precision_recall_curve
import matplotlib.pyplot as plt

if sys.stdout.encoding != 'UTF-8':
	sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
if sys.stderr.encoding != 'UTF-8':
	sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

def main():
	start_time = time.time()

	data_path = os.path.abspath(sys.argv[1])
	controlled_dict_path = os.path.abspath(sys.argv[2])

	load_data(data_path)
	load_controlled_dict(controlled_dict_path)
	count()
	true_classes, est_classes, decision_functions = naive_bayes()

	# results display options
	# feature_ranking()
	# document_ranking()
	# plot_metrics(true_classes,decision_functions)

	print("Time: " + str(time.time() - start_time))

def load_data(path):
	data = open(path, 'r', encoding='utf-8')
	global m_restaurants
	m_restaurants = json.load(data)
	data.close()

def load_controlled_dict(path):
	global controlled_dict
	file = open(path, "r", encoding="utf-8")
	cd = file.read().split("\n")

	for word in cd:
		controlled_dict[word] = 0

	file.close()

# go through corpus to estimate probabilities
def count():
	global num_neg_docs
	global num_pos_docs

	for i in range(len(m_restaurants)):
		for review in m_restaurants[i]["Reviews"]:
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

def naive_bayes():
	true_classes = []
	est_classes = []

	for i in range(len(m_restaurants)):
		for review in m_restaurants[i]["Reviews"]:
			if float(review["Overall"]) < 4.0:
				true_classes.append(0)
			else:
				true_classes.append(1)

			est_class, decision_function = linear(review)

			est_classes.append(est_class)
			decision_functions.append(decision_function)

	return(true_classes, est_classes, decision_functions)

def linear(review):
	f_x = math.log(p("y=1","")/p("y=0",""))

	for x in review["Content"]:
		f_x += math.log(p("w|y=1",x)) - math.log(p("w|y=0",x))

	f.append([f_x,review["ReviewID"]])

	return(sgn(f_x),f_x)

# support functions

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
	delta = 0.01
	if w in dictionary:
		return((dictionary[w] + delta)/(2+delta*(len(total_vocab))))
	else:
		return(delta/(2+delta*(len(total_vocab))))

def check_dictionary(dictionary, key):
	if key in dictionary:
		dictionary[key] += 1
	else:
		dictionary[key] = 1

# display results

def plot_metrics(t,e):
	precision, recall, _ = precision_recall_curve(t,e)
	average_precision = average_precision_score(t,e)

	plt.step(recall, precision, color="b", alpha=0.01, where="post")
	plt.fill_between(recall, precision, step="post", alpha=0.01, color="b")
	plt.xlabel("Recall")
	plt.ylabel("Precision")

	plt.show()

def document_ranking():
	f_sorted = sorted(f, reverse=True)

	for i in f_sorted:
		print(str(i[0]) + "," + str(i[1]))

def feature_ranking():
	for w in controlled_dict:
		controlled_dict[w] = math.log(float(p("w|y=1",w)/p("w|y=0",w)))
	
	cd_sorted = [[w,controlled_dict[w]] for w in sorted(controlled_dict, key=controlled_dict.get, reverse=True)]

	for i in range(len(cd_sorted)):
		print(cd_sorted[i][0], cd_sorted[i][1])

# global variables

total_vocab = {}
pos_vocab = {}
neg_vocab = {}
controlled_dict = {}
f = []
m_restaurants = []

global num_pos_docs
num_pos_docs = 0
global num_neg_docs
num_neg_docs = 0

main()
