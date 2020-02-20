import re
import boto3
import string
import sys
from discord.utils import get
from cogs.config import *

discord_id_re = re.compile('<@.?[0-9]*?>')
suspicious_characters = set(string.punctuation
                                  .replace('@', '')
                                  .replace('#', '')
                                  .replace('\'', '')
                            )


def mentions_to_names(s, bot):
    """Converts the text of a mention to the format @<User#0000>"""
    matches = discord_id_re.findall(s)
    for mention in matches:
        discord_id = mention.replace('<@', '') \
            .replace('>', '') \
            .replace('i', '') \
            .replace('!', '') \
            .replace('&', '')

        user = get(bot.get_all_members(), id=int(discord_id))
        if user:
            s = s.replace(mention, f'@{user.name}#{user.discriminator}')
        else:
            s = s.replace(mention, '@UNKNOWN_USER')

    return s


def likely_a_bot_command(s):
    """If the first word in a message contains punctuation (with some exceptions) and the last character in the
    word is not punctuation, assume the first word is a bot prefix so we can filter it."""
    first_word = s.split(' ')[0]
    if any((c in suspicious_characters) for c in first_word[:-1]) and \
       not any((c in string.punctuation) for c in first_word[-1]):
        return first_word
    else:
        return False


def find_common_prefixes(filters):
    """For example, take ['df!generate', 'df!help', ...] and return ['df!']"""
    common_prefixes = []
    for fil in filters:
        if any((prefix in fil) for prefix in common_prefixes):
            continue

        min_idx = sys.maxsize
        for p in suspicious_characters:
            idx = fil.find(p)
            if (idx > -1) and (idx < min_idx):
                min_idx = idx

        common_prefixes.append(fil[:min_idx+1])

    return common_prefixes


def upload_to_s3(file_name):
    s3 = boto3.resource('s3',
                        aws_access_key_id=aws_access_key_id,
                        aws_secret_access_key=aws_secret_access_key)

    s3.Object(aws_s3_bucket_prefix, f'{file_name}'.strip('./tmp/')).upload_file(f'{file_name}')
