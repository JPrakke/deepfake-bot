import discord
from discord.ext import commands
from cogs import db_queries
from cogs import plot_activity
import s3fs
import gzip
import re
from cogs import config
import boto3
import botocore
import json
import os
import logging
import datetime as dt

logger = logging.getLogger(__name__)


class PlotCommands(commands.Cog):
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

    async def wordcloud_request(self, ctx, bot, subject, data_uid, filters, dirty):
        await bot.wait_until_ready()

        # Pack up the data
        request_data = {
            "data_uid": data_uid,
            "filters": filters,
            "dirty": dirty
        }
        payload = json.dumps(request_data)

        # Invoke the lambda function
        try:
            start_time = dt.datetime.now()
            response = self.lambda_client.invoke(
                FunctionName=config.lambda_wordcloud_name,
                InvocationType='RequestResponse',
                LogType='Tail',
                Payload=payload,
            )
            end_time = dt.datetime.now()
            logger.info(f'Wordcloud lambda function processed. Time elapsed: {end_time - start_time}')
            res_str = response['Payload'].read().decode('utf-8')
            res_json = json.loads(res_str)
        except botocore.exceptions.ReadTimeoutError:
            await ctx.message.channel.send(
                'Wordcloud request timed out. Maybe try again. You can also report this here:'
                f' {config.report_issue_url}'
            )
            return

        # In case it fails...
        try:
            status_code = res_json['statusCode']
        except KeyError:
            status_code = 0

        # More logic in case it fails...
        if status_code == 200:
            image_file_name = res_json['image_file_name']
            total_messages = res_json['total_messages']
            filtered_messages = res_json['filtered_messages']
        else:
            await ctx.message.channel.send(
                'Hmmm... I seem to be having trouble with your request. Maybe try again. You can also report this here:'
                f' {config.report_issue_url}'
            )
            return

        # If everything is ok...
        if image_file_name:

            # Get the file from S3
            with open(f'./tmp/{image_file_name}', 'wb') as f:
                self.s3_client.download_fileobj(config.aws_s3_bucket_prefix, image_file_name, f)

            # Send it to discord
            await ctx.message.channel.send(f'Here are {subject.name}\'s favorite words:',
                                           file=discord.File(f'./tmp/{image_file_name}'))
            # Cleanup
            os.remove(f'./tmp/{image_file_name}')

            # Message...
            if dirty:
                await ctx.send('What a potty mouth!')

            await ctx.send(f'Using {filtered_messages} of {total_messages} messages.')

        # In case there are no swear words
        elif dirty:
            await ctx.send(f'Hmmm... {subject.name} doesn\'t seem to use bad language.')


    @commands.command()
    async def wordcloud(self, ctx, *, subject: discord.Member):
        """Uploads a wordcloud image if a data set exists for the mentioned subject"""
        if subject:
            data_id = await db_queries.get_latest_dataset(self.session, ctx, subject)
            if data_id:
                filters = db_queries.find_filters(self.session, ctx, subject)
                await ctx.send('Wordcloud request submitted...')
                await self.wordcloud_request(ctx, self.bot, subject, data_id, filters, False)
        else:
            await ctx.message.channel.send(f'Usage: `df!wordcloud User#0000`')

    @commands.command()
    async def dirtywordcloud(self, ctx, *, subject: discord.Member):
        """Uploads a wordcloud image of curse words if a dataset has been extracted for the mentioned subject"""
        if subject:
            data_id = await db_queries.get_latest_dataset(self.session, ctx, subject)
            if data_id:
                filters = db_queries.find_filters(self.session, ctx, subject)
                await ctx.send('Wordcloud request submitted...')
                await self.wordcloud_request(ctx, self.bot, subject, data_id, filters, True)
        else:
            await ctx.send(f'Usage: `df!dirtywordcloud User#0000`')

    @commands.command()
    async def activity(self, ctx, *, subject: discord.Member):
        """Uploads time series and pie charts image if a data set exists for the mentioned subject"""
        if subject:
            data_id = await db_queries.get_latest_dataset(self.session, ctx, subject)
            if data_id:
                # Make the time series chart
                file_name = plot_activity.time_series_chart(data_id, subject.name)
                await ctx.message.channel.send('', file=discord.File(file_name, file_name))
                os.remove(file_name)

                # Make the pie charts
                pie_chart_channels, pie_chart_days = plot_activity.pie_charts(data_id, subject.name)
                await ctx.message.channel.send('', file=discord.File(pie_chart_channels, pie_chart_channels))
                await ctx.message.channel.send('', file=discord.File(pie_chart_days, pie_chart_days))
                os.remove(pie_chart_channels)
                os.remove(pie_chart_days)
                await ctx.message.channel.send(
                      """Don\'t see a channel? Make sure I have permission to read it before running `df!extract`.""")

        else:
            await ctx.message.channel.send(f'Usage: `df!activity User#0000`')

    @commands.command()
    async def countword(self, ctx, subject: discord.Member = None, word: str = None):
        """Counts the number of times a subject has used a word."""
        if subject and word:
            data_id = await db_queries.get_latest_dataset(self.session, ctx, subject)
            if data_id:
                # Read the file from S3
                s3 = s3fs.S3FileSystem(key=config.aws_access_key_id,
                                       secret=config.aws_secret_access_key)
                with s3.open(f'{config.aws_s3_bucket_prefix}/{data_id}-text.dsv.gz', mode='rb') as f:
                    g = gzip.GzipFile(fileobj=f)
                    content = g.read().decode().replace(config.unique_delimiter, ' ')

                # Regex for the word in question
                expr = f'[ ]{word.lower()}[.!? ]'
                reg = re.compile(expr)
                count = len(reg.findall(content.lower()))

                await ctx.message.channel.send(f"User {subject.name} has said {word} {count} times.")
