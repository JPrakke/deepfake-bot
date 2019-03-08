import os, uuid, gzip, boto3, discord, asyncio, common.config
import datetime as dt
import queries

# Need to make this a background task
async def extract_and_analyze(ctx, user_mention, bot):
    await bot.wait_until_ready()

    channel = ctx.message.channel

    extraction_id = str(uuid.uuid4().hex)
    text_file_name = f'../tmp/{extraction_id}-text.dsv.gz'
    timestamp_file_name = f'../tmp/{extraction_id}-timestamps.txt.gz'
    channel_file_name = f'../tmp/{extraction_id}-channels.tsv.gz'

    message_counters = []
    channels = []
    timestamps = []
    print(f'Extracting chat history for {user_mention}...')
    start_time = dt.datetime.now()
    with gzip.open(text_file_name, 'wb') as f:
        for channel in ctx.message.server.channels:
            try:
                message_counter = 0
                async for message in bot.logs_from(channel, limit=10**7):
                    if message.author == user_mention:
                        message_counter += 1
                        result = str(message.content + common.config.unique_delimiter)
                        timestamps.append(int(message.timestamp.timestamp()))
                        f.write(result.encode())
                if message_counter > 0:
                    channels.append(channel.name)
                    message_counters.append(message_counter)
            except Exception:
                continue

    with gzip.open(timestamp_file_name, 'wb') as f:
        for t in sorted(timestamps):
            f.write(f'{t}\n'.encode())

    with gzip.open(channel_file_name, 'wb') as f:
        f.write('channel,count\n'.encode())
        for i in range(len(channels)):
            f.write(f'{channels[i]},{message_counters[i]}\n'.encode())

    end_time = dt.datetime.now()
    print(f'{sum(message_counters)} messages extracted.')
    print(f'Logs copied to tmp folder. Time elapsed = {end_time - start_time}')

    # S3
    print('Uploading to S3...')
    start_time = dt.datetime.now()
    upload_to_s3(text_file_name)
    upload_to_s3(timestamp_file_name)
    upload_to_s3(channel_file_name)
    end_time = dt.datetime.now()
    print(f'Files uploaded to S3: {extraction_id}. Time elapsed = {end_time - start_time}')

    # TODO: add to database

    # Cleanup local disk
    os.remove(text_file_name)
    os.remove(timestamp_file_name)
    os.remove(channel_file_name)

def upload_to_s3(file_name):
    s3 = boto3.resource('s3',
                        aws_access_key_id=common.config.aws_access_key_id,
                        aws_secret_access_key=common.config.aws_secret_access_key)

    s3.Object(common.config.aws_s3_bucket_prefix, f'{file_name}'.strip('../tmp/')).upload_file(f'{file_name}')
