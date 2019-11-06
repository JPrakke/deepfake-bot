from discord.ext import commands
from cogs import config
import boto3
import botocore
import json
import datetime as dt
import logging

logger = logging.getLogger(__name__)


class LambdaCommand(commands.Cog):
    """Base class for invoking AWS Lambda funtions."""
    def __init__(self, bot):
        self.bot = bot
        self.parent_cog = self.bot.get_cog('DeepFakeBot')
        self.session = self.parent_cog.session
        self.lambda_client = boto3.client('lambda', region_name='us-east-1')
        self.s3_client = boto3.client('s3')

    async def cog_check(self, ctx):
        connection_ok = await self.parent_cog.cog_check(ctx)
        self.session = self.parent_cog.session
        return connection_ok

    async def invoke_lambda(self, ctx, lambda_name, request_data, command_name):

        await self.bot.wait_until_ready()
        payload = json.dumps(request_data)

        # Invoke the lambda function
        try:
            start_time = dt.datetime.now()
            response = self.lambda_client.invoke(
                FunctionName=lambda_name,
                InvocationType='RequestResponse',
                LogType='Tail',
                Payload=payload,
            )
            end_time = dt.datetime.now()
            logger.info(f'{command_name} lambda function processed. Time elapsed: {end_time - start_time}')
            res_str = response['Payload'].read().decode('utf-8')
            res_json = json.loads(res_str)
        except botocore.exceptions.ReadTimeoutError:
            await ctx.message.channel.send(
                f'{command_name} request timed out. Maybe try again. You can also report this here:'
                f' {config.report_issue_url}'
            )
            return

        # In case it fails...
        try:
            status_code = res_json['statusCode']
        except KeyError:
            return

        # More logic in case it fails...
        if status_code == 200:
            return res_json
        else:
            return
