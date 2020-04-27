import discord
from discord.ext import commands
from cogs import db_queries
from cogs import lambda_commands
from cogs import config
import os
import logging
import uuid
import json

logger = logging.getLogger(__name__)


class PlotCommands(lambda_commands.LambdaCommand):

    async def activity_reponse(self, ctx, subject, image_file_names):
        """What the bot should do if activity plots are successfully generated"""
        for image_file_name in image_file_names:
            await ctx.send(f'', file=discord.File(f'./tmp/{image_file_name}'))
            os.remove(f'./tmp/{image_file_name}')

    async def wordcloud_response(self, ctx, subject, image_file_name, response_file_name, dirty=False):
        """What the bot should do if a wordcloud is  successfully generated"""
        with open(f'./tmp/{response_file_name}') as f:
            response = json.loads(f.read())

        if not dirty:
            total_messages = response['total_messages']
            filtered_messages = response['filtered_messages']
            await ctx.send(f'Here are {subject}\'s favorite words:', file=discord.File(f'./tmp/{image_file_name}'))
            await ctx.send(f'Using {filtered_messages} of {total_messages} messages.')
        else:
            swears = response['swears']
            if swears:
                await ctx.send(f'Here are {subject.name}\'s favorite words:',
                               file=discord.File(f'./tmp/{image_file_name}'))
                await ctx.send('What a potty mouth!')
            else:
                await ctx.send(f'Hmmm... {subject.name} doesn\'t seem to use bad language')

        # Cleanup
        os.remove(f'./tmp/{image_file_name}')
        os.remove(f'./tmp/{response_file_name}')

    async def process_activity(self, ctx, subject, data_uid):
        """Function for handling activity plots. Need to make this separate from the command so it can be called by
        df!generate"""
        image_uid = str(uuid.uuid4().hex)

        payload = {
            'data_uid': data_uid,
            'user_name': subject.name,
            'image_uid': image_uid
        }

        activity_file_name = f'{image_uid}-activity.png'
        file_name_channels = f'{image_uid}-pie-chart-channels.png'

        expected_files = [activity_file_name, file_name_channels]

        # Invoke the lambda function
        ok = await self.get_lambda_files(config.lambda_activity_name, payload,
                                         expected_files, 10,
                                         self.activity_reponse, ctx, subject, expected_files)

        if not ok:
            await ctx.send(
                           f'Activity plot request timed out. Maybe try again. You can also report this here:'
                           f' {config.report_issue_url}'
                          )
        elif ctx.invoked_with == 'generate':
            # Start the next step in the process...

            await ctx.send('Starting task 3 of 4...')
            filters = db_queries.find_filters(self.parent_cog.session, ctx, subject)
            await ctx.send('Wordcloud request submitted...')
            await self.process_wordcloud(ctx, subject, data_uid, filters)

    async def process_wordcloud(self, ctx, subject, data_uid, filters, dirty=False):
        """Function for handling wordcloud plots. Need to make this separate from the command so it can be called by
        df!generate"""

        wordcloud_file_name = str(uuid.uuid4().hex) + '-word-cloud.png'
        response_file_name = wordcloud_file_name.replace('.png', '.json')

        payload = {'data_uid': data_uid,
                   'filters': filters,
                   'wordcloud_file_name': wordcloud_file_name,
                   'dirty': dirty}

        # Invoke the lambda function
        ok = await self.get_lambda_files(config.lambda_wordcloud_name, payload,
                                         [wordcloud_file_name, response_file_name], 10,
                                         self.wordcloud_response, ctx, subject, wordcloud_file_name,
                                         response_file_name, dirty)

        if not ok:
            await ctx.send(
                           f'Wordcloud request timed out. Maybe try again. You can also report this here:'
                           f' {config.report_issue_url}'
                          )
        elif ctx.invoked_with == 'generate':
            # Start the last step in the process...

            await ctx.send('Starting task 4 of 4...')
            state_size, newline = db_queries.get_markov_settings(self.parent_cog.session, ctx, subject)
            markov_cog = self.bot.get_cog('ModelCommands')
            await ctx.send('Markovify request submitted...')
            await markov_cog.process_markovify(ctx, subject, data_uid, filters, state_size, newline)

    @commands.command()
    @commands.cooldown(10, 300, type=commands.BucketType.user)
    async def wordcloud(self, ctx, *, subject: discord.Member = None):
        """Uploads a wordcloud image if a data set exists for the mentioned subject"""
        if subject:
            data_id = await db_queries.get_latest_dataset(self.session, ctx, subject)
            if data_id:
                filters = db_queries.find_filters(self.session, ctx, subject)
                await ctx.send('Wordcloud request submitted...')
                await self.process_wordcloud(ctx, subject, data_id, filters)
        else:
            await ctx.message.channel.send(f'Usage: `df!wordcloud <User#0000>`')

    @commands.command()
    @commands.cooldown(10, 300, type=commands.BucketType.user)
    async def dirtywordcloud(self, ctx, *, subject: discord.Member = None):
        """Uploads a wordcloud image of curse words if a dataset has been extracted for the mentioned subject"""
        if subject:
            data_id = await db_queries.get_latest_dataset(self.session, ctx, subject)
            if data_id:
                filters = db_queries.find_filters(self.session, ctx, subject)
                await ctx.send('Wordcloud request submitted...')
                await self.process_wordcloud(ctx, subject, data_id, filters, True)
        else:
            await ctx.send(f'Usage: `df!dirtywordcloud <User#0000>`')

    @commands.command()
    @commands.cooldown(10, 300, type=commands.BucketType.user)
    async def activity(self, ctx, *, subject: discord.Member = None):
        """Uploads time series and pie charts image if a data set exists for the mentioned subject"""
        if subject:
            data_id = await db_queries.get_latest_dataset(self.session, ctx, subject)
            if data_id:
                await ctx.send('Activity plot request submitted...')
                await self.process_activity(ctx, subject, data_id)
        else:
            await ctx.message.channel.send(f'Usage: `df!activity <User#0000>`')
