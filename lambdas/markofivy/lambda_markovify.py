import markovify
import boto3
import json
import os
import gzip


# TODO: upload model artifacts to S3
def lambda_handler(event, context):
    # Read in arguments / event data
    data_uid = event['data_uid']
    new_line = event['new_line']
    filters = event['filters']
    state_size = event['state_size']
    number_responses = event['number_responses']

    # Download the data set from S3
    text_file_name = f'{data_uid}-text.dsv.gz'
    aws_s3_bucket_prefix = os.environ['DEEPFAKE_S3_BUCKET_PREFIX']
    s3 = boto3.resource('s3')
    s3.Bucket(aws_s3_bucket_prefix) \
        .download_file(text_file_name, '/tmp/' + text_file_name)

    # Decompress
    with open('/tmp/' + text_file_name, 'rb') as f:
        g = gzip.GzipFile(fileobj=f)
        content = g.read().decode(). \
            split('11a4b96a-ae8a-45f9-a4db-487cda63f5bd')

    # Apply filters
    filtered_content = []
    for i in content:
        include = True
        for j in filters:
            if j in i:
                include = False
                break
        if include:
            filtered_content.append(i)

    # Generate the model
    if new_line:
        text_model = markovify.NewlineText('\n'.join(filtered_content),
                                           state_size=state_size)
    else:
        text_model = markovify.Text('\n'.join(filtered_content),
                                    state_size=state_size)

    # Generate responses
    responses = []
    for i in range(number_responses):
        responses.append(text_model.make_sentence(tries=100))

    return {
        'statusCode': 200,
        'body': responses
    }
