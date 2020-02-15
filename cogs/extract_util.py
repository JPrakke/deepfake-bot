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
import asyncio

# Need to limit the number of messages for larger servers
MAX_CHANNEL_MESSAGES = 10**5

logger = logging.getLogger(__name__)
discord_id_re = re.compile('<@.?[0-9]*?>')


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


async def extract_chat_history(ctx, subject, bot):
    """Background task for reading chat history and uploading to S3"""
    await bot.wait_until_ready()

    logger.info(f'Extracting chat history for {subject.name}...')
    start_time = dt.datetime.now()

    # Prevent the user from have more than one extraction task run at once
    bot.get_cog('DeepFakeBot').extraction_task_users.append(ctx.author.id)

    # Setup file names
    extraction_id = str(uuid.uuid4().hex)
    text_file_name = f'./tmp/{extraction_id}-text.dsv.gz'
    channel_file_name = f'./tmp/{extraction_id}-channels.csv.gz'

    # Setup initial parameters for our loop
    timestamps, channel_names, accessible_channels, unreadable_channels, message_counter = [], [], [], [], 0

    # Determine the number of text channels and which ones the bot can read
    readable_channels = list(filter(lambda x: hasattr(x, 'history'), ctx.message.guild.channels))
    for channel in readable_channels:
        try:
            async for message in channel.history(limit=1):
                _ = message.content
            accessible_channels.append(channel)
        except Exception as e:
            if str(e).startswith('403'):
                unreadable_channels.append(channel.name)
            else:
                logger.error(str(e))

    msg = f'Found {len(accessible_channels)} text channels that I have permission to read. This task could take up to '\
          f'{len(accessible_channels) * 3} minutes.'

    bot.loop.create_task(
        ctx.send(msg)
    )

    # Open a text file and start looping through each channel messages
    with gzip.open(text_file_name, 'wb') as f:
        for channel in accessible_channels:
            channel_counter = 0
            author_counter = 0
            try:
                logger.info(f'Processing channel: {channel.name} on {ctx.guild.name}')
                start_time_channel = dt.datetime.now()
                async for message in channel.history(limit=MAX_CHANNEL_MESSAGES):
                    channel_counter += 1
                    try:
                        if message.author == subject:
                            author_counter += 1
                            message_counter += 1
                            result = str(mentions_to_names(message.content, bot) + unique_delimiter)
                            timestamps.append(int(message.created_at.timestamp()))
                            channel_names.append(channel.name)
                            f.write(result.encode())
                    except Exception as e:
                        logger.error(str(e))

                end_time_channel = dt.datetime.now()
                logger.info(f'{channel.name} processed in {end_time_channel - start_time_channel} seconds')

            except Exception as e:
                logger.error(str(e))

            if author_counter > 0:
                msg = f'Found {author_counter} of {channel_counter} messages written by '\
                      f'{subject.name} in `#{channel.name}`'
                logger.info(msg)
                bot.loop.create_task(
                    ctx.send(msg)
                )

    with gzip.open(channel_file_name, 'wb') as f:
        f.write('timestamp,channel\n'.encode())
        for i in range(len(channel_names)):
            f.write(f'{timestamps[i]},{channel_names[i]}\n'.encode())

    end_time = dt.datetime.now()
    logger.info(f'{message_counter} total messages extracted.')
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
    db_queries.create_data_set(session, ctx, subject, extraction_id)

    # Bot replies
    await bot.wait_until_ready()
    await asyncio.sleep(1)
    await ctx.send(f'Extraction complete for {subject}. Found {message_counter} total messages:',
                   files=[discord.File(text_file_name), discord.File(channel_file_name)])

    if unreadable_channels:
        if len(unreadable_channels) == 1:
            await ctx.send(f'Note: some messages may have been missed since there is a '
                           'channel that I do not have permission to read.')
        else:
            await ctx.send(f'Note: some messages may have been missed since there are {len(unreadable_channels)} '
                           'channels that I do not have permission to read.')
        chs = ', '.join(unreadable_channels)
        logger.info(f'Unreadable channels: {chs}')

    # Disk cleanup
    os.remove(text_file_name)
    os.remove(channel_file_name)

    # Allow the user to execute this command again
    bot.get_cog('DeepFakeBot').extraction_task_users.remove(ctx.author.id)

    if ctx.invoked_with == 'generate':
        # Start the next step in the process...

        await ctx.send('Starting task 2 of 4...')
        plots_cog = bot.get_cog('PlotCommands')
        await ctx.send('Activity plot request submitted...')
        await plots_cog.process_activity(ctx, subject, extraction_id)


def upload_to_s3(file_name):
    s3 = boto3.resource('s3',
                        aws_access_key_id=aws_access_key_id,
                        aws_secret_access_key=aws_secret_access_key)

    s3.Object(aws_s3_bucket_prefix, f'{file_name}'.strip('./tmp/')).upload_file(f'{file_name}')
