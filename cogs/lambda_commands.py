from discord.ext import commands
from cogs import config
import boto3
import botocore
from botocore.errorfactory import ClientError
import json
import datetime as dt
import logging
import os
import asyncio

logger = logging.getLogger(__name__)
MAX_ATTEMPTS = 10


class LambdaCommand(commands.Cog):
    """Base class for invoking AWS Lambda funtions."""
    def __init__(self, bot):
        self.bot = bot
        self.parent_cog = self.bot.get_cog('CoreCommands')
        self.session = self.parent_cog.session
        self.lambda_client = boto3.client('lambda', region_name='us-east-1')
        self.s3_client = boto3.client('s3')

    async def cog_check(self, ctx):
        connection_ok = await self.parent_cog.cog_check(ctx)
        self.session = self.parent_cog.session
        return connection_ok

    async def get_lambda_files(self, lambda_name: str, request_data: dict, expected_files: list
                               , delay: int, bot_response, *args):
        """Invokes a lambda function asynchronously and copies the result files from S3 to the ./tmp folder."""

        payload = json.dumps(request_data)

        # Invoke the lambda function
        start_time = dt.datetime.now()

        try:
            response = self.lambda_client.invoke(
                FunctionName=lambda_name,
                InvocationType='Event',
                LogType='Tail',
                Payload=payload,
            )
        except botocore.exceptions.ReadTimeoutError:
            return

        # In case it fails...
        try:
            status_code = response['StatusCode']
            if status_code != 202:
                return
        except KeyError:
            return

        # If everything is ok, start checking S3 for the expected files
        for attempt in range(MAX_ATTEMPTS):

            # Need to allow some time for the lambda function to process
            await asyncio.sleep(delay)

            # Try to grab all the files
            got_all_files = True
            for file_name in expected_files:
                try:
                    # Get the file from S3
                    if not os.path.exists(f'./tmp/{file_name}'):
                        self.s3_client.download_file(config.aws_s3_bucket_prefix, file_name, f'./tmp/{file_name}')

                except ClientError:
                    got_all_files = False
                    logger.info(f'Attempt {attempt + 1} of {MAX_ATTEMPTS} failed. Lambda function not complete.')

            if got_all_files:
                break

        end_time = dt.datetime.now()
        logger.info(f'{lambda_name} processed. Time elapsed: {end_time - start_time}')

        if got_all_files:

            # Run the function for bot response
            await bot_response(*args)
            return True
