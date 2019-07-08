from discord import utils
import s3fs
import gzip
import boto3
from robot.config import *
from textgenrnn import textgenrnn


# Use this to identify a user by mention or name#discriminator
def get_subject(bot, ctx, subject_string, command_name):
    mentions = ctx.message.mentions

    if len(mentions) == 1:
        return mentions[0], ''
    elif len(mentions) > 1:
        return False, f'One at a time please. Usage: `df!{command_name} User#0000` <args>'

    else:
        try:
            subject_name = subject_string.split('#')[0]
            subject_discriminator = subject_string.split('#')[1]
            p = bot.get_all_members()
            found_members = filter(lambda m: (m.discriminator == subject_discriminator)
                                   and (m.name == subject_name), p)
            subject = utils.get(found_members)
            if subject:
                return subject, ''
            else:
                return False, f'Hmmm... I can\'t seem to find {subject_string}'

        except IndexError:
            return False, f'Hmmm... I can\'t seem to find {subject_string}'


# Counts the number of words in a data set
def count_word(data_id, word):
    s3 = s3fs.S3FileSystem(key=aws_access_key_id,
                           secret=aws_secret_access_key)
    with s3.open(f'{aws_s3_bucket_prefix}/{data_id}-text.dsv.gz', mode='rb') as f:
        g = gzip.GzipFile(fileobj=f)
        content = g.read().decode().replace(unique_delimiter, ' ')

    # Regex for the word in question
    expr = f'[ ]{word.lower()}[.!? ]'
    reg = re.compile(expr)
    return len(reg.findall(content.lower()))


# Copies model files from S3 to tmp folder
def download_model_files(data_uid, job_id):
    weights_file_name = f'{data_uid}-{str(job_id)}_weights.hdf5'
    vocab_file_name = f'{data_uid}-{str(job_id)}_vocab.json'
    config_file_name = f'{data_uid}-{str(job_id)}_config.json'

    s3 = boto3.resource('s3',
                        aws_access_key_id=aws_access_key_id,
                        aws_secret_access_key=aws_secret_access_key)

    s3.Bucket(aws_s3_bucket_prefix).download_file(weights_file_name, f'./tmp/{weights_file_name}')
    s3.Bucket(aws_s3_bucket_prefix).download_file(vocab_file_name, f'./tmp/{vocab_file_name}')
    s3.Bucket(aws_s3_bucket_prefix).download_file(config_file_name, f'./tmp/{config_file_name}')


# Need to make this a background task
async def infer(ctx, data_uid, job_id, bot):
    await bot.wait_until_ready()

    print(f'Loading model...')
    download_model_files(data_uid, job_id)
    print('Model downloaded...')
    weights_file_name = f'{data_uid}-{str(job_id)}_weights.hdf5'
    vocab_file_name = f'{data_uid}-{str(job_id)}_vocab.json'
    config_file_name = f'{data_uid}-{str(job_id)}_config.json'

    # TODO: optimize this..., pre-load available models as a background test
    model = textgenrnn(name=f'{data_uid}-{str(job_id)}',
                       weights_path=f'./tmp/{weights_file_name}',
                       vocab_path=f'./tmp/{vocab_file_name}',
                       config_path=f'./tmp/{config_file_name}'
                       )

    print('Model files read. Generating...')
    result = model.generate(return_as_list=True)[0]
    await ctx.message.channel.send(result)
