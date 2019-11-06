import discord
from discord.ext import commands
from cogs import db_queries
from cogs import lambda_commands
from cogs import config
import os
import logging

logger = logging.getLogger(__name__)


class PlotCommands(lambda_commands.LambdaCommand):

    async def process_image_request(self, ctx, subject, request_data, lambda_name, command_name, message):

        # Invoke the lambda function
        res_json = await self.invoke_lambda(ctx, lambda_name, request_data, command_name)

        # Read the results
        if res_json:
            image_file_names = res_json['image_file_names']
            try:
                total_messages = res_json['total_messages']
                filtered_messages = res_json['filtered_messages']
            except KeyError:
                total_messages = None
                filtered_messages = None
        else:
            await ctx.message.channel.send(
                'Hmmm... I seem to be having trouble with your request. Maybe try again. You can also report this here:'
                f' {config.report_issue_url}'
            )
            return

        # Get the "dirty" flag
        try:
            dirty = request_data['dirty']
        except KeyError:
            dirty = False

        # If everything is ok...
        for image_file_name in image_file_names:

            # Get the file from S3
            with open(f'./tmp/{image_file_name}', 'wb') as f:
                self.s3_client.download_fileobj(config.aws_s3_bucket_prefix, image_file_name, f)

            # Send it to discord
            await ctx.message.channel.send(message, file=discord.File(f'./tmp/{image_file_name}'))
            # Cleanup
            os.remove(f'./tmp/{image_file_name}')

            # Message...
            if dirty:
                await ctx.send('What a potty mouth!')
            if total_messages:
                await ctx.send(f'Using {filtered_messages} of {total_messages} messages.')

        # In case there are no swear words
        if len(image_file_names) == 0 and dirty:
            await ctx.send(f'Hmmm... {subject.name} doesn\'t seem to use bad language.')

    @commands.command()
    async def wordcloud(self, ctx, *, subject: discord.Member):
        """Uploads a wordcloud image if a data set exists for the mentioned subject"""
        if subject:
            data_id = await db_queries.get_latest_dataset(self.session, ctx, subject)
            if data_id:
                filters = db_queries.find_filters(self.session, ctx, subject)
                await ctx.send('Wordcloud request submitted...')
                request_data = {
                    "data_uid": data_id,
                    "filters": filters,
                    "dirty": False
                }
                await self.process_image_request(ctx, subject, request_data, config.lambda_wordcloud_name,
                                                 'Wordcloud', f'Here are {subject.name}\'s favorite words:')
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
                request_data = {
                    "data_uid": data_id,
                    "filters": filters,
                    "dirty": True
                }
                await self.process_image_request(ctx, subject, request_data, config.lambda_wordcloud_name,
                                                 'Wordcloud', f'Here are {subject.name}\'s favorite swear words:')
        else:
            await ctx.send(f'Usage: `df!dirtywordcloud User#0000`')

    @commands.command()
    async def activity(self, ctx, *, subject: discord.Member):
        """Uploads time series and pie charts image if a data set exists for the mentioned subject"""
        if subject:
            data_id = await db_queries.get_latest_dataset(self.session, ctx, subject)
            if data_id:
                await ctx.send('Activity plot request submitted...')
                request_data = {
                    "data_uid": data_id,
                    "user_name": subject.name
                }
                await self.process_image_request(ctx, subject, request_data, config.lambda_activity_name,
                                                 'activity plot', '')
                await ctx.message.channel.send(
                      """Don\'t see a channel? Make sure I have permission to read it before running `df!extract`.""")

        else:
            await ctx.message.channel.send(f'Usage: `df!activity User#0000`')
