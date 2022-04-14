# Twitter Bot for @WhoFundsTheWar

Twitter Bot for `https://twitter.com/WhoFundsTheWar`.

Twitter Bot publishes status of companies' business activities in Russia.

The Bot tracks data from the Yale CELI research - updated continuously by Jeffrey Sonnenfeld and his team of experts, research fellows, and students at the Yale Chief Executive Leadership Institute to reflect new announcements from companies.

Bot uses AWS SQS to store messages before tweeting them.

## Usage

1. `virtualenv venv;venv/Scripts/activate;pip install -r requirements.txt` - set up the project (on Windows).
2. `cp .env.example .env` - create .env file and assign proper values.
3. `python src/create_tweets.py` - populate the SQS queue with tweet messages.
4. `python src/send_tweets.py` - retrieve tweet messages from SQS one-by-one, post them to Twitter and remove from SQS (to change the throttle rate change the `PAUSE_TIME_IN_SECONDS` variable).

## Sources

- `https://www.yalerussianbusinessretreat.com/` - as a main source of information
- `https://airtable.com/shri4fzaMzXrQ3ZHp/tbloSNFhgc3BjkuC8` - for supplementary data, e.g. twitter handles
