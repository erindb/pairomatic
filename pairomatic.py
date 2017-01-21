import json
import random
from time import strftime
from itertools import chain
from collections import Counter

## imports for email:
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
## for if you want to send emails from a secure email address:
# import getpass
import smtplib

import sys

if "-s" in sys.argv:
	mode = "send"
else:
	mode = "test"

def print_sample_email(data):
	salutation = 'Hi {{personA}} and {{personB}}!'
	email_content = "".join(open(data['email_content_file']).readlines()[1:])
	email_subject = open(data['email_content_file']).readlines()[0][:-1]
	body = salutation + email_content
	print "========================email template========================"
	print "subject: " + email_subject
	print "--------------------------------------------------------------"
	print body,
	print "=============================================================="

def main():
	with open('data.json') as data_file:
		data = json.load(data_file)

	print_sample_email(data)

	## decide pairings for this week based on data in json file
	pairs_this_week = creat_pairs_for_week(data)
	week = {
		'pairs': pairs_this_week,
		'day': strftime("%Y-%m-%d"),
		'time': strftime("%H:%M:%S"),
		'email_sent': False
	}

	## attempt to send emails and record if success
	try:
		send_emails(pairs_this_week, data)
		week['email_sent'] = True
		# add new week to history
		data['history'].append(week)

		if (mode=="send" and mode!="test"):
			with open('data.json', 'w') as outfile:
				json.dump(data, outfile, sort_keys=True, indent=4, separators=(',', ': '))
				print "updating history"
		else:
			print "you are in test mode. no data written to data.json. see test.out for what would have been written to data.json."
			with open('test.out', 'w') as outfile:
				json.dump(data, outfile, sort_keys=True, indent=4, separators=(',', ': '))

	except smtplib.SMTPAuthenticationError:
		print 'authentication error: emails not sent'

def creat_pairs_for_week(data):
	def pair_string(pair):
		pair.sort()
		return "~".join(pair)

	def pair_list(pair_string):
		return pair_string.split("~")

	def get_pair_counts(history, this_week):
		# filter so that only emails that actually got sent count
		relevant_history = filter(lambda x: x['email_sent'], history)
		pair_lists = map(lambda x: x['pairs'], relevant_history)
		pairs = list(chain.from_iterable(pair_lists))
		# filter so that only pairs of people in this week are counted
		relevant_pairs = filter(
			lambda pair: (pair[0] in this_week) and (pair[1] in this_week),
			pairs)
		pair_strings = map(lambda x: pair_string(x), relevant_pairs)
	  	pair_counts = Counter(pair_strings)
		return pair_counts
		return involves_person

	def get_previous_partners(person, pair_counts):
		pairs = map(pair_list, list(pair_counts.elements()))
		relevant_pairs = filter(lambda pair: (pair[0] == person) or (pair[1] == person), pairs)
		partners = map(lambda pair: pair[1] if (pair[0]==person) else pair[0], relevant_pairs)
		return partners

	def exclude(pair_counts, pair_to_exclude):
		pairs = map(pair_list, list(pair_counts.elements()))
		remaining_pairs = filter(lambda pair: (
			(pair[0] != pair_to_exclude[0]) and
			(pair[0] != pair_to_exclude[1]) and
			(pair[1] != pair_to_exclude[0]) and
			(pair[1] != pair_to_exclude[1])), pairs)
		return Counter(map(pair_string, remaining_pairs))

	def most_common(a_counter):
		max_count = a_counter.most_common(1)[0][1]
		most_common_pair_counts = filter(lambda x: x[1]==max_count, a_counter.most_common())
		return map(lambda x: x[0], most_common_pair_counts)

	def least_common(a_counter):
		min_count = a_counter.most_common()[-1][1]
		least_common_pair_counts = filter(lambda x: x[1]==min_count, a_counter.most_common())
		return map(lambda x: x[0], least_common_pair_counts)

	def choose_extra_person(possible_doubles, pair_counts):
		pairs = map(pair_list, list(pair_counts.elements()))
		#list(chain.from_iterable(pair_lists))
		people_tokens = list(chain.from_iterable(pairs))
		never_paired_doubles = [person for person in possible_doubles if not person in people_tokens]
		if (len(never_paired_doubles)>0):
			return random.choice(never_paired_doubles)
		else:
			double_people_tokens = filter(lambda x: x in possible_doubles, people_tokens)
			double_counts = Counter(double_people_tokens)
			least_comon_doubles = least_common(double_counts)
			return random.choice(least_comon_doubles)

	def subset(a_counter, a_list):
		elements = a_counter.elements()
		return Counter(filter(lambda x: x in a_list, elements))

	people_this_week = data['people']['this_week']
	pair_counts = get_pair_counts(data['history'], people_this_week)
	already_paired = []
	unpaired = [person for person in people_this_week]
	doubles = [person for person in people_this_week if person in data['people']['doubles']]

	pairs_this_week = []

	while len(unpaired)>1:
		unpaired_pair_counts = subset(pair_counts, unpaired)
		if len(unpaired_pair_counts)>0:
			pair_to_repair = random.choice(most_common(unpaired_pair_counts))
			people_to_repair = pair_to_repair.split("~")
		else:
			people_to_repair = unpaired[0:1]
		for person_to_repair in people_to_repair:
			previous_partners = get_previous_partners(person_to_repair, pair_counts)
			never_paired_partners = [partner for partner in people_this_week if ((not partner in previous_partners) and (partner != person_to_repair))]
			# any person who the person_to_pair hasn't been paired with (who hasn't already been paired this week) would be a great partner
			never_paired_potential_partners = filter(lambda x: not x in  already_paired, never_paired_partners)
			if (len(never_paired_potential_partners)>0):
				new_partner = random.choice(never_paired_potential_partners)
			else:
				# the partner (who hasn't already been paired this week and) who the parson_to_pair has been paired with least is best
				potential_partners = filter(lambda x: not x in  already_paired, previous_partners)
				new_partner = Counter(previous_partners).most_common()[-1][0]
			new_pair = [person_to_repair, new_partner]
			#add new pair to this week's pairs
			pairs_this_week.append(new_pair)
			already_paired.append(person_to_repair)
			already_paired.append(new_partner)
			unpaired = [person for person in people_this_week if not person in already_paired]

	if len(unpaired) == 1:
		person_to_repair = unpaired[0]
		possible_doubles = [person for person in doubles if person != person_to_repair]
		extra_person = choose_extra_person(possible_doubles, pair_counts)
		new_partner = extra_person
		new_pair = [person_to_repair, new_partner]
		#add new pair to this week's pairs
		pairs_this_week.append(new_pair)
		already_paired.append(person_to_repair)
		already_paired.append(new_partner)
		unpaired = [person for person in people_this_week if not person in already_paired]

	return pairs_this_week

def send_emails(pairs, data):

	my_email_address = data['source_account']['email_address']
	my_user_id = data['source_account']['user_id']
	password = data['source_account']['password']
	email_addresses = data['people']['emails']
	namesub_dict = data['people']['namesub']

	def namesub(person):
		if person in namesub_dict.keys():
			return namesub_dict[person]
		else:
			return person

	def sendemail(from_addr, to_addr_list, cc_addr_list, bcc_addr_list, subject, message, login,
	    password):
		header  = 'From: %s\n' % from_addr
		header += 'To: %s\n' % ','.join(to_addr_list)
		header += 'Cc: %s\n' % ','.join(cc_addr_list)
		header += 'Subject: %s\n\n' % subject
		message = header + message

		server = smtplib.SMTP_SSL('smtp.gmail.com:465')
		server.login(login,password)
		problems = server.sendmail(from_addr, to_addr_list + cc_addr_list + bcc_addr_list, message)
		server.quit()

	def emailPair(personA, personB):
		salutation = 'Hi ' + namesub(personA) + ' and ' + namesub(personB) + '!'
		email_content = "".join(open(data['email_content_file']).readlines()[1:])
		email_subject = open(data['email_content_file']).readlines()[0][:-1]
		body = salutation + email_content

		if (mode=="send" and mode!="test"):
			sendemail(from_addr    = my_email_address, 
					  to_addr_list = [email_addresses[personA], email_addresses[personB]],
					  cc_addr_list = [my_email_address],
					  bcc_addr_list = [],
					  subject      = email_subject, 
					  message      = body, 
					  login        = my_user_id, 
					  password     = password)

			print "sent to", personA, "and", personB
		else:
			print "you are in test mode. if you had included -s, i would have sent to ", personA, "and", personB

	for pair in pairs:
		personA = pair[0]
		personB = pair[1]
		# print namesub(personA)
		# print namesub(personB)
		emailPair(personA, personB)

main()