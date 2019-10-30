import os

# AWS Credentials
aws_access_key_id = os.environ['DEEPFAKE_AWS_ACCESS_KEY_ID']
aws_secret_access_key = os.environ['DEEPFAKE_SECRET_ACCESS_KEY']
aws_s3_bucket_prefix = 'deepfake-discord-bot'

# Amazon RDS
database_url = os.environ['DEEPFAKE_DATABASE_STRING']

# Need a unique delimiter to keep massages in flat text.
unique_delimiter = '11a4b96a-ae8a-45f9-a4db-487cda63f5bd'

report_issue_url = 'https://github.com/rustygentile/deepfake-bot/issues/new'
