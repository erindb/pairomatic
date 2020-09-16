#! /usr/bin/env python
# coding=UTF-8

import json
import random
from time import strftime
from itertools import chain
from collections import Counter
import argparse

# to automate slack
import urllib.request
import os
import json

def send_slack_message(text, webhook_url):
    if webhook_url is not None:
        r = urllib.request.Request(webhook_url,
                                   data=json.dumps({'text': text}).encode('utf-8'),
                                   headers={
                                       'Content-Type': 'application/json'
                                   },
                                   method='POST')
        with urllib.request.urlopen(r) as f:
            status = str(f.status)
    else:
        status = 'not sent - no webhook URL'
 
    print('Slack message: {} (status: {})'.format(text, status))

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument("--slack", action="store_true", help="slack")
	parser.add_argument("--save",  action="store_true", help="save data")
	parser.add_argument("--i", type=str, help="input data file", default="data.json")
	args = parser.parse_args()

	with open(args.i) as data_file:
		data = json.load(data_file)

	## decide pairings for this week based on data in json file
	pairs_this_week = creat_pairs_for_week(data)
	week = {
		'pairs': pairs_this_week,
		'day': strftime("%Y-%m-%d"),
		'time': strftime("%H:%M:%S"),
		'email_sent': False
	}

	if args.slack:
		send_slack_message(
			"Here are the pairs for this week!\n" +
			"\n".join(
				["{} & {}".format(pair[0], pair[1]) for pair in pairs_this_week]
			) +
			"\n" +
			data["slack"]["message"]["post"],
			data["slack"]["webhook_url"]
		)
		week["email_sent"] = True

		data['history'].append(week)
		with open(args.i, 'w') as outfile:
			json.dump(data, outfile, sort_keys=True, indent=4,
				separators=(',', ': '))
			print("updating history")

	for pair in pairs_this_week:
		print("{} & {}".format(namesub(pair[0], data), namesub(pair[1], data)))

def pair_string(pair):
	pair.sort()
	return "~".join(pair)

def pair_list(pair_string):
	return pair_string.split("~")

def most_common(a_counter):
	max_count = a_counter.most_common(1)[0][1]
	def is_max(x):
		return x[1]==max_count
	most_common_pair_counts = [x for x in a_counter.most_common() if is_max(x)]
	return [x[0] for x in most_common_pair_counts]

def pair_contains_person_in_list(pair, a_list):
	people_in_pair = pair.split("~")
	return people_in_pair[0] in a_list or people_in_pair[1] in a_list

def subset_one(a_counter, a_list):
	elements = a_counter.elements()
	return Counter([x for x in elements if pair_contains_person_in_list(x, a_list)])

def least_common(a_counter):
	if len(a_counter.most_common()) == 0:
		return [pair_list(x)[0] for x in list(a_counter.elements())]
	else:
		min_count = a_counter.most_common()[-1][1]
		def is_min(x):
			return x[1]==min_count
		least_common_pair_counts = [x for x in a_counter.most_common() if is_min(x)]
		return [x[0] for x in least_common_pair_counts]

def get_pair_counts(history, this_week):
	pairs_history = [p for x in history for p in x['pairs']]
	# filter so that only pairs of people in this week are counted
	relevant_pairs_history = [pair for pair in pairs_history if (pair[0] in this_week) and (pair[1] in this_week)]
	pair_strings_history = [pair_string(x) for x in relevant_pairs_history]
	all_pairs = []
	for personA in this_week:
		for personB in this_week:
			if personA < personB:
				all_pairs.append("{}~{}".format(personA, personB))
	pair_counts = Counter(pair_strings_history + all_pairs)
	return pair_counts

def creat_pairs_for_week(data):
	people_this_week = data['people']['this_round']
	pair_counts = get_pair_counts(data['history'], people_this_week)

	# set up lists of who is paired vs unpaired
	already_paired = set()
	unpaired = set(people_this_week)
	doubles = set([person for person
		in people_this_week
		if person in data['people']['doubles']])
	pairs_this_week = []
	def pairable(x):
		return not x in already_paired

	if len(unpaired) % 2 == 1 and len(doubles) == 0:
		raise Exception("There's an odd number this week! Either remove/add someone from the list or get a volunteer to double up.")

	while len(unpaired)>1:
		new_pairs = []
		if len(unpaired) == 2:
			new_pairs.append(unpaired)
		elif len(unpaired) == 1:
			person_to_pair = unpaired[0]
			if person_to_pair in doubles:
				# break up a different pair if the remaining person is willing to double up
				past_pair = pairs_this_week.pop()
				new_pairs.append([person_to_pair, past_pair[0]])
				new_pairs.append([person_to_pair, past_pair[1]])
			else:
				# or pair the remaining person up with whoever they've met with least who's willing to meet twice
				possible_doubles = [person for person
					in doubles
					if person != person_to_pair]
				extra_person = choose_extra_person(possible_doubles, pair_counts)
				new_partner = extra_person
				new_pairs.append([person_to_pair, new_partner])
		else:
			# find the pairs that have been paired together the most and pair them with someone else
			unpaired = [person for person
				in people_this_week
				if pairable(person)]
			unpaired_pair_counts = get_pair_counts(data['history'], unpaired)
			most_commonly_paired = [x for pair_string in most_common(unpaired_pair_counts) for x in pair_list(pair_string)]
			random.shuffle(most_commonly_paired)
			person_to_pair = most_commonly_paired[0]
			potential_new_partners = [
				[x for x in pair_list(s) if x != person_to_pair][0] for s
				in least_common(subset_one(unpaired_pair_counts, [person_to_pair]))
			]
			random.shuffle(potential_new_partners)
			new_pairs.append([person_to_pair, potential_new_partners[0]])
		#add new pair to this week's pairs
		for new_pair in new_pairs:
			pairs_this_week.append(new_pair)
			already_paired.add(new_pair[0])
			already_paired.add(new_pair[1])
		unpaired = [person for person
			in people_this_week
			if pairable(person)]

	return pairs_this_week

def namesub(person, data):
	namesub_dict = data['people']['namesub']
	if person in namesub_dict.keys():
		return namesub_dict[person]
	else:
		return person

main()
