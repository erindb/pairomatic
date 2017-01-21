# README

A script to automatically send pairing emails to people so they can meet up and talk about their work.

## Requirements

* Python 2.7.6 (possibly other versions would work, too)
* an email account that [does not need to be secure](https://support.google.com/accounts/answer/6010255?hl=en)
* a `data.json` file similar to `sample-data.json` that includes:
	- a file name with the email content (first line is subject, rest of file is body of email) under `email_content_file`
	- login information for said account under `source_account`
	- a key of people's emails to in `people` > `emails`
	- who to send emails to this round in `people` > `this_round`
	- a key of nicknames, etc. for how to actually refer to people in the email salutation in `people` > `namesub`
	- people willing to meet twice in one round in `people` > `doubles`

## Usage

Once data file is specified, run:

	python pairomatic.py

By default, this will run in test mode and not actually send emails to people or re-write the history in your `data.json` file. It will print what would have been added to the `data.json` file to a new file `test.out`. If you want to actually send the emails, run:

	python pairomatic.py -s

In order to run automatically on the 1st of the month at 2pm, include the following cronjob:

	0 14 1 * * bash ~/path/to/pairomatic/pairomatic.sh

As you run `pairomatic`, it will update the `history` in `data.json` to keep track of who has met with who. It will try not to pair the same people together if there are other people they haven't met with yet.
