import os

# AWS Credentials
aws_access_key_id = os.environ['DEEPFAKE_AWS_ACCESS_KEY_ID']
aws_secret_access_key = os.environ['DEEPFAKE_SECRET_ACCESS_KEY']

# AWS Resource Names
aws_s3_bucket_prefix = 'deepfake-discord-bot'
lambda_markov_name = 'deepfake-bot-markovify'
lambda_wordcloud_name = 'deepfake-bot-wordcloud'
lambda_activity_name = 'deepfake-bot-activity'

# Amazon RDS
database_url = os.environ['DEEPFAKE_DATABASE_STRING']

# Need a unique delimiter to keep messages in flat text.
unique_delimiter = '11a4b96a-ae8a-45f9-a4db-487cda63f5bd'

report_issue_url = 'https://github.com/rustygentile/deepfake-bot/issues/new'
deepfake_owner_id = 551864836917821490
version = '1.1.7'
