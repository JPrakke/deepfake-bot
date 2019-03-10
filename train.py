import sys
import s3fs
import gzip
from textgenrnn import textgenrnn
import common.config


# Simple training job script. Adds models to tmp folder.
# TODO: add queries, figure out how to host this and make it a bot command...
def train(data_id):
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

    textgen = textgenrnn(name=f'./tmp/{data_id}')
    train_function = textgen.train_from_file

    # Download from S3
    s3 = s3fs.S3FileSystem(key=common.config.aws_access_key_id,
                           secret=common.config.aws_secret_access_key)

    with s3.open(f'{common.config.aws_s3_bucket_prefix}/{data_id}-text.dsv.gz', mode='rb') as f:
        g = gzip.GzipFile(fileobj=f)
        content = g.read().decode().replace(common.config.unique_delimiter, '\n')

    # Copy to tmp folder
    with open(f'./tmp/{data_id}-train.txt', 'w', encoding='utf-8') as f:
        f.write(content)

    # Start training
    try:
        train_function(
            file_path=f'./tmp/{data_id}-train.txt',
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
    except:
        print(f'Problem training model for {data_id}')


if __name__ == '__main__':
    train(sys.argv[1])
