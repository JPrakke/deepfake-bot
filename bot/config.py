import os

# Credentials
aws_access_key_id = os.environ['DEEPFAKE_AWS_ACCESS_KEY_ID']
aws_secret_access_key = os.environ['DEEPFAKE_SECRET_ACCESS_KEY']
aws_s3_bucket_prefix = os.environ['DEEPFAKE_S3_BUCKET_PREFIX']

# Need a unique delimiter to keep massages in flat text.
unique_delimiter = os.environ['DEEPFAKE_DELIMITER']
