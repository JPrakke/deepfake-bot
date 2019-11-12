import markovify
import boto3
import gzip

UNIQUE_DELIMITER = '11a4b96a-ae8a-45f9-a4db-487cda63f5bd'


def lambda_handler(event, context):
    # Read in arguments / event data
    data_uid = event['data_uid']
    model_uid = event['model_uid']
    new_line = event['new_line']
    filters = event['filters']
    state_size = event['state_size']
    number_responses = event['number_responses']

    # Download the data set from S3
    text_file_name = f'{data_uid}-text.dsv.gz'
    aws_s3_bucket_prefix = 'deepfake-discord-bot'
    s3 = boto3.resource('s3')
    s3.Bucket(aws_s3_bucket_prefix) \
        .download_file(text_file_name, '/tmp/' + text_file_name)

    # Decompress
    with open('/tmp/' + text_file_name, 'rb') as f:
        g = gzip.GzipFile(fileobj=f)
        content = g.read().decode(). \
            split(UNIQUE_DELIMITER)

    # Apply filters
    if filters == ['']:
        filtered_content = content
    else:
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
        responses.append(str(text_model.make_sentence(tries=100)))
    if len(responses) > 1:
        result = UNIQUE_DELIMITER.join(responses)
    else:
        result = 'Failed :('

    # Write results to compressed file
    model_file_name = f'{model_uid}-markov-model.json.gz'
    with gzip.open(f'/tmp/{model_file_name}', 'wb') as f:
        f.write(text_model.to_json().encode())

    # Write sample responses to file
    sample_repsonse_file_name = f'{model_uid}-sample-responses.txt'
    with open(f'/tmp/{sample_repsonse_file_name}', 'w', encoding='utf-8') as f:
        f.write(result)

    # Upload to S3
    s3.Object(aws_s3_bucket_prefix, model_file_name) \
        .upload_file(f'/tmp/{model_file_name}')

    s3.Object(aws_s3_bucket_prefix, sample_repsonse_file_name) \
        .upload_file(f'/tmp/{sample_repsonse_file_name}')

    return {
        'statusCode': 200,
        'body': responses,
        'model_uid': model_uid
    }
