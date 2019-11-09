import uuid
import gzip
import boto3
import datetime as dt
from cogs import db_queries
from cogs.config import *
import discord
import logging
import re
from discord.utils import get

logger = logging.getLogger(__name__)
discord_id_re = re.compile('<@.?[0-9]*?>')


def mentions_to_names(s, bot):
    """Converts the text of a mention to the format @<User#0000>"""
    matches = discord_id_re.findall(s)
    for mention in matches:
        discord_id = mention.replace('<@', '') \
            .replace('>', '') \
            .replace('i', '') \
            .replace('!', '')

        user = get(bot.get_all_members(), id=int(discord_id))
        if user:
            s = s.replace(mention, f'@{user.name}#{user.discriminator}')
        else:
            s = s.replace(mention, '@UNKNOWN_USER')

    return s


async def extract_chat_history(ctx, user_mention, bot):
    """Background task for reading chat history and uploading to S3"""
    await bot.wait_until_ready()

    extraction_id = str(uuid.uuid4().hex)
    text_file_name = f'./tmp/{extraction_id}-text.dsv.gz'
    channel_file_name = f'./tmp/{extraction_id}-channels.csv.gz'

    channels, timestamps, message_counter = [], [], 0
    logger.info(f'Extracting chat history for {user_mention}...')
    start_time = dt.datetime.now()
    with gzip.open(text_file_name, 'wb') as f:
        for channel in ctx.message.guild.channels:
            try:
                async for message in channel.history(limit=10**7):
                    try:
                        if message.author == user_mention:
                            message_counter += 1
                            result = str(mentions_to_names(message.content, bot) + unique_delimiter)
                            timestamps.append(int(message.created_at.timestamp()))
                            channels.append(channel.name)
                            f.write(result.encode())
                    except Exception as e:
                        logger.error(str(e))
            except Exception as e:
                logger.error(str(e))

    with gzip.open(channel_file_name, 'wb') as f:
        f.write('timestamp,channel\n'.encode())
        for i in range(len(channels)):
            f.write(f'{timestamps[i]},{channels[i]}\n'.encode())

    end_time = dt.datetime.now()
    logger.info(f'{message_counter} messages extracted.')
    logger.info(f'Logs copied to tmp folder. Time elapsed = {end_time - start_time}')

    # S3
    logger.info('Uploading to S3...')
    start_time = dt.datetime.now()
    upload_to_s3(text_file_name)
    upload_to_s3(channel_file_name)
    end_time = dt.datetime.now()
    logger.info(f'Files uploaded to S3: {extraction_id}. Time elapsed = {end_time - start_time}')

    # Add to database
    session = bot.get_cog('ConnectionManager').session
    db_queries.create_data_set(session, ctx, user_mention, extraction_id)

    # Bot reply
    await ctx.send(f'Extraction complete for {user_mention}. Found {message_counter} messages:',
                   files=[discord.File(text_file_name), discord.File(channel_file_name)])

    # Cleanup local disk
    os.remove(text_file_name)
    os.remove(channel_file_name)

    if ctx.invoked_with == 'generate':
        await ctx.send('Starting task 2 or 4...')


def upload_to_s3(file_name):
    s3 = boto3.resource('s3',
                        aws_access_key_id=aws_access_key_id,
                        aws_secret_access_key=aws_secret_access_key)

    s3.Object(aws_s3_bucket_prefix, f'{file_name}'.strip('./tmp/')).upload_file(f'{file_name}')
