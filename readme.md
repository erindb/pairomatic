# README

A script to automatically send slack messages to a channel so ppl can meet up and
talk about their work.

## Requirements

* Python 3
* a slack webhook URL
* a `.json` file similar to `sample-data.json` that includes the following
data:
	- slack webhood and message content
	- information about people under the key `people`
		- who to pair up on **this round** (may vary round by round who is
		available) under the key `this_round`
		- a key of nicknames, etc. for how to actually refer to people, under the key `namesub`
		- people willing to meet twice in one round under the key `doubles`

## Usage

Once data file is specified, run:

	python pairomatic.py --i sample-data.json

You can replace `sample-data.json` with your own data file.

By default, this will run in test mode and not actually send messages
or re-write the history in your `data.json` file. It will print what would have
been added to the `data.json` file to a new file `test.out`. If you want to
actually send the message, run:

	python pairomatic.py --i sample-data.json --slack

In order to run automatically on the 1st of the month at 2pm, include the
following cronjob:

	0 14 1 * * python ~/path/to/pairomatic/pairomatic.py --i data.json --slack

As you run `pairomatic`, it will update the `history` in `data.json` to keep
track of who has met with who. It will try not to pair the same people together
if there are other people they haven't met with yet.
