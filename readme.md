# README

A script to automatically send pairing emails to people so they can meet up and talk about their work.

## Requirements

* Python 2.7.6 (possibly other versions would work, too)
* an email account that [does not need to be secure](https://support.google.com/accounts/answer/6010255?hl=en)
* a `data.json` file similar to `sample-data.json` that includes:
	- login information for said account under `source_account`
	- a key of people's emails to in `people` > `emails`
	- who to send emails to this week in `people` > `this_week`
	- a key of nicknames, etc. for how to actually refer to people in the email salutation in `people` > `namesub`
	- people willing to meet twice in one week in `people` > `doubles`

## Installation

Once data file is specified, run:

	python pair-o-matic.py

In order to run automatically once every two weeks on Tuesdays at 17:39, include the following cronjob:

	39 17 * * 2 bash ~/cocolab/pair-o-matic/pair-o-matic.sh