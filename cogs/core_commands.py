import logging
import discord
from discord.ext import commands
import boto3
import asyncio
import random
import glob
from cogs import config
from cogs import extract_task
from cogs import db_queries
from cogs.db_connection import DeepFakeBotConnectionError
from cogs.config import *

logger = logging.getLogger(__name__)


class CoreCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.session = None
        self.generate_subject = None
        self.extraction_task_users = []
        self.servers_where_typing = []
        self.s3_client = boto3.client('s3')

        # Cleanup the /tmp folder
        old_files = glob.glob('./tmp/*.*')
        for file in old_files:
            os.remove(file)

        with open('./tmp/.gitkeep', 'w') as fp:
            pass

    async def delete_after_5_min(self, file_name):
        """Background task for cleaning up a file after downloading"""
        await asyncio.sleep(300)
        os.remove(file_name)

    async def cog_check(self, ctx):
        """Refreshes the database connection and registers the user if not already done."""
        connection_manager = self.bot.get_cog('ConnectionManager')
        try:
            connection_manager.refresh_connection()
        except DeepFakeBotConnectionError:
            await ctx.message.channel.send(
                  'Ruh roh! I seem to be having some issues. Try running that command again later')
            return False

        self.session = connection_manager.session
        await db_queries.register_trainer(self.session, ctx)
        return True

    @commands.Cog.listener()
    async def on_ready(self):
        logger.info('Logged in as')
        logger.info(self.bot.user.name)
        logger.info(self.bot.user.id)
        logger.info('------')

    @commands.command(hidden=True)
    async def newsletter(self, ctx, msg):
        """Sends a DM to all registered users"""
        if ctx.author.id != deepfake_owner_id:
            await ctx.send('You don\'t have permission to use that command.')
        else:
            logger.info(msg)
            registered_users = db_queries.get_all_registered_users(self.session)
            for u in registered_users:
                user = discord.utils.get(self.bot.get_all_members(), id=u.discord_id)
                if user:
                    await user.send(msg + '\nIf you would no longer like to receive these messages, '
                                    'reply with `df!unsubscribe`.')

    @commands.command()
    @commands.cooldown(2, 60, type=commands.BucketType.user)
    async def unsubscribe(self, ctx):
        """Removes you from newsletter list"""
        success = db_queries.change_subscription_status(self.session, ctx, False)
        if success:
            await ctx.send('You will no longer receive newsletter messages.')

    @commands.command()
    @commands.cooldown(2, 60, type=commands.BucketType.user)
    async def subscribe(self, ctx):
        """Adds you to newsletter list"""
        success = db_queries.change_subscription_status(self.session, ctx, True)
        if success:
            await ctx.send('You will now receive newsletter messages.')

    @commands.command()
    @commands.cooldown(5, 300, type=commands.BucketType.user)
    async def extract(self, ctx, *, subject: discord.Member = None):
        """Extracts chat history of a subject"""
        if subject:
            if ctx.author.id in self.extraction_task_users:
                await ctx.send('Please wait until your other extraction task is complete.')
            else:
                db_queries.register_subject(self.session, ctx, subject)
                await ctx.send(
                    f'Extracting chat history for {subject.name}...'
                )
                self.bot.loop.create_task(
                    extract_task.extract_chat_history(ctx, subject, self.bot)
                )
        else:
            await ctx.send('Usage: `df!extract <User#0000>`')

    @commands.command()
    @commands.cooldown(5, 300, type=commands.BucketType.user)
    async def generate(self, ctx, *, subject: discord.Member = None):
        """Runs all of the process steps needed to generate a model"""
        if subject:
            if ctx.author.id in self.extraction_task_users:
                await ctx.send('Please wait until your other extraction task is complete.')
            else:
                db_queries.register_subject(self.session, ctx, subject)
                await ctx.send('Starting task 1 of 4...')
                await ctx.send(
                    f'Extracting chat history for {subject.name}...'
                )
                self.bot.loop.create_task(
                    extract_task.extract_chat_history(ctx, subject, self.bot)
                )
        else:
            await ctx.send('Usage: `df!generate <User#0000>`')

    @commands.command()
    @commands.cooldown(2, 60, type=commands.BucketType.user)
    async def stats(self, ctx):
        """Shares some stats with you"""
        stats = db_queries.statistics(self.session)
        result = 'Here are some stats about me:\n```'
        for k in stats.keys():
            result += f'{k}: {stats[k]}\n'
        result += f'Extraction tasks in progress: {len(self.extraction_task_users)}'
        result += '```'

        await ctx.send(result)

    @commands.command()
    @commands.cooldown(10, 60)
    async def impersonate(self, ctx, subject: discord.Member = None):
        """Reply in the style of another user"""

        if subject is None:
            await ctx.send('Usage: `df!impersonate <@User#0000>`')
            return

        # Don't impersonate more than one person at a time on a server
        if ctx.message.guild.id in self.servers_where_typing:
            await ctx.author.send('Sorry, I\'m busying impersonating someone else right now. Try again when I\'m done.')
            return

        # Check if there's a model for that user
        model_uid = await db_queries.get_latest_markov_model(self.session, ctx, subject)
        if model_uid:

            sample_response_file = f'{model_uid}-sample-responses.txt'

            # Download the file from S3 and delete it after 5 minutes
            if not os.path.exists(f'./tmp/{sample_response_file}'):
                self.s3_client.download_file(config.aws_s3_bucket_prefix, sample_response_file,
                                             f'./tmp/{sample_response_file}')
                self.bot.loop.create_task(
                    self.delete_after_5_min(sample_response_file)
                )

            # Pick a random response
            with open(f'./tmp/{sample_response_file}') as f:
                responses = f.read().split(config.unique_delimiter)
                res = responses[random.randrange(1000)]

            # Change the bot nickname
            if subject.nick is None:
                await ctx.message.guild.me.edit(nick=subject.display_name)
            else:
                await ctx.message.guild.me.edit(nick=subject.nick)

            # Type the response
            self.servers_where_typing.append(ctx.message.guild.id)
            async with ctx.channel.typing():
                await asyncio.sleep(len(res) / 5)
                await ctx.send(res)

            # Cleanup / reset
            await asyncio.sleep(5)
            self.servers_where_typing.remove(ctx.message.guild.id)
            await ctx.message.guild.me.edit(nick='DeepfakeBot')
