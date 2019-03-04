import os, uuid, gzip, boto3, discord, asyncio, config
import datetime as dt

# Need to make this a background task
async def extract_user_chats(ctx, user_mention, bot):
    await bot.wait_until_ready()

    channel = ctx.message.channel

    extraction_id = str(uuid.uuid4())
    file_name = extraction_id + '-train.tsv.gz'

    start_time = dt.datetime.now()
    print(f'Extracting chat history for {user_mention}...')
    with gzip.open('./tmp/' + file_name, 'wb') as f:
        async for message in bot.logs_from(channel, after=dt.datetime.now() - dt.timedelta(30)):
            if message.author.mention == user_mention:
                result = str(
                    int(message.timestamp.timestamp())) + '\t' + message.content + config.unique_delimiter + '\n'
                f.write(result.encode())

    end_time = dt.datetime.now()
    print(f'Logs copied to tmp folder. Time elapsed = {end_time - start_time}')

    # S3
    print('Uploading to S3...')
    start_time = dt.datetime.now()
    upload_to_s3(file_name)
    end_time = dt.datetime.now()
    print(f'File uploaded to S3: {file_name}. Time elapsed = {end_time - start_time}')

def upload_to_s3(file_name):
    s3 = boto3.resource('s3',
                        aws_access_key_id=config.aws_access_key_id,
                        aws_secret_access_key=config.aws_secret_access_key)

    s3.Object(config.aws_s3_bucket_prefix, file_name).upload_file(f'./tmp/{file_name}')
