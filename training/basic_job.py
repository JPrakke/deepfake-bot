import s3fs
import gzip
import boto3
from textgenrnn import textgenrnn
from common.config import *
from training import queries


# Simple training job. Adds models to s3 folder.
# TODO: Figure out how to host this and make it a bot command...
def train(data_id, model_path, filters):
    model_cfg = {
        'word_level': False,
        'rnn_size': 128,
        'rnn_layers': 3,
        'rnn_bidirectional': False,
        'max_length': 30,
        'max_words': 10000
    }

    train_cfg = {
        'line_delimited': True,
        'num_epochs': 20,
        'gen_epochs': 5,
        'train_size': 0.8,
        'dropout': 0.0,
        'validation': False,
        'is_csv': False
    }

    textgen = textgenrnn(name=f'{model_path}/{data_id}')
    train_function = textgen.train_from_file

    # Download from S3
    s3 = s3fs.S3FileSystem(key=aws_access_key_id,
                           secret=aws_secret_access_key)

    # Extract
    with s3.open(f'{aws_s3_bucket_prefix}/{data_id}-text.dsv.gz', mode='rb') as f:
        g = gzip.GzipFile(fileobj=f)
        content = g.read().decode()

    # Apply pre-processing. I'm sure there's a more pythonic way to do this...
    content_array = content.split(unique_delimiter)
    filter_words = filters.split(',')
    filtered_content = []
    for message in content_array:
        include = True
        for pattern in filter_words:
            if pattern in message:
                include = False
                break
        if include:
            filtered_content.append(message)

    # Logging
    print(f'Writing data set. {len(filtered_content)} of {len(content_array)} original messaged used...')

    # Generate a filtered data set in tmp folder
    with open(f'{model_path}/{data_id}-train.txt', 'w', encoding='utf-8') as f:
        for line in filtered_content:
            f.write(line + '\n')

    # Start training
    job_failed = True
    job_id = queries.start_job(data_id)
    try:
        train_function(
            file_path=f'{model_path}/{data_id}-train.txt',
            new_model=True,
            num_epochs=train_cfg['num_epochs'],
            gen_epochs=train_cfg['gen_epochs'],
            batch_size=1024,
            train_size=train_cfg['train_size'],
            dropout=train_cfg['dropout'],
            validation=train_cfg['validation'],
            is_csv=train_cfg['is_csv'],
            rnn_layers=model_cfg['rnn_layers'],
            rnn_size=model_cfg['rnn_size'],
            rnn_bidirectional=model_cfg['rnn_bidirectional'],
            max_length=model_cfg['max_length'],
            dim_embeddings=100,
            word_level=model_cfg['word_level'])
        job_failed = False
    except:
        print(f'Problem training model for {data_id}')

    if job_failed:
        queries.job_failed(job_id)
    else:

        # Model files
        config_file = f'{model_path}/{data_id}_config.json'
        vocab_file = f'{model_path}/{data_id}_vocab.json'
        weights_file = f'{model_path}/{data_id}_weights.hdf5'

        # Add them to s3
        s3 = boto3.resource('s3',
                            aws_access_key_id=aws_access_key_id,
                            aws_secret_access_key=aws_secret_access_key)

        s3.Object(aws_s3_bucket_prefix, f'{data_id}-{str(job_id)}_config.json').upload_file(config_file)
        s3.Object(aws_s3_bucket_prefix, f'{data_id}-{str(job_id)}_vocab.json').upload_file(vocab_file)
        s3.Object(aws_s3_bucket_prefix, f'{data_id}-{str(job_id)}_weights.hdf5').upload_file(weights_file)

        # Record training in database
        queries.job_finished(job_id)

        # Cleanup Disk
        os.remove(config_file)
        os.remove(vocab_file)
        os.remove(weights_file)
