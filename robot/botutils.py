from discord import utils
import s3fs
import gzip
import boto3
from robot.config import *


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
