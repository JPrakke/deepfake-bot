import logging
import discord
from discord.ext import commands
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
    @commands.cooldown(1, 60, type=commands.BucketType.user)
    async def unsubscribe(self, ctx):
        """Removes you from newsletter list"""
        success = db_queries.change_subscription_status(self.session, ctx, False)
        if success:
            await ctx.send('You will no longer receive newsletter messages.')

    @commands.command()
    @commands.cooldown(1, 60, type=commands.BucketType.user)
    async def subscribe(self, ctx):
        """Adds you from newsletter list"""
        success = db_queries.change_subscription_status(self.session, ctx, True)
        if success:
            await ctx.send('You will now receive newsletter messages.')

    @commands.command()
    @commands.cooldown(1, 60, type=commands.BucketType.user)
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
    @commands.cooldown(1, 60, type=commands.BucketType.user)
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
    @commands.cooldown(1, 60, type=commands.BucketType.user)
    async def stats(self, ctx):
        """Shares some stats with you"""
        stats = db_queries.statistics(self.session)
        result = 'Here are some stats about me:\n```'
        for k in stats.keys():
            result += f'{k}: {stats[k]}\n'
        result += f'Extraction tasks in progress: {len(self.extraction_task_users)}'
        result += '```'

        await ctx.send(result)
