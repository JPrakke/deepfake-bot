import discord
import os
from discord.ext import commands
from robot import queries
from robot import botutils
from robot import plot_wordcloud
from robot import plot_activity


class PlotCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.parent_cog = self.bot.get_cog('DeepFakeBot')
        self.session = self.parent_cog.session

    async def cog_check(self, ctx):
        connection_ok = await self.parent_cog.cog_check(ctx)
        self.session = self.parent_cog.session
        return connection_ok

    @commands.command()
    async def wordcloud(self, ctx, *, subject: discord.Member):
        """Uploads a wordcloud image if a data set has been extracted for the mentioned subject"""
        if subject:
            data_id = await queries.get_latest_dataset(self.session, ctx, subject)
            if data_id:
                filters = queries.find_filters(self.session, ctx, subject)
                file_name, n_messages, n_filtered = plot_wordcloud.generate(data_id, filters)
                await ctx.message.channel.send(f'Here are {subject.name}\'s favorite words:',
                                               file=discord.File(file_name, file_name))
                os.remove(file_name)
                await ctx.message.channel.send(f'Using {n_filtered} of {n_messages} messages.')
        else:
            await ctx.message.channel.send(f'Usage: `df!wordcloud User#0000`')

    @commands.command()
    async def activity(self, ctx, *, subject: discord.Member):
        """Uploads a time series and bar charts image if a dataset exists for the mentioned subject"""

        if subject:
            data_id = await queries.get_latest_dataset(self.session, ctx, subject)
            if data_id:
                file_name = plot_activity.generate(data_id, subject.name)
                await ctx.message.channel.send('', file=discord.File(file_name, file_name))
                os.remove(file_name)

                bar_file_name, bar_file_name_log = plot_activity.bar_charts(data_id, subject.name)

                # Only make bar charts if more than one channel
                if bar_file_name and bar_file_name_log:
                    await ctx.message.channel.send('', file=discord.File(bar_file_name, bar_file_name))
                    await ctx.message.channel.send('', file=discord.File(bar_file_name_log, bar_file_name_log))
                    os.remove(bar_file_name)
                    os.remove(bar_file_name_log)
                    await ctx.message.channel.send(
                      """Don\'t see a channel? Make sure I have permission to read it before running `df!extract`.""")

        else:
            await ctx.message.channel.send(f'Usage: `df!activity User#0000`')

    @commands.command()
    async def dirtywordcloud(self, ctx, *, subject: discord.Member):
        """Uploads a wordcloud image of curse words if a dataset has been extracted for the mentioned subject"""
        if subject:
            data_id = await queries.get_latest_dataset(self.session, ctx, subject)
            if data_id:
                file_name = plot_wordcloud.generate_dirty(data_id)
                if file_name:
                    await ctx.message.channel.send(f'Here are {subject.name}\'s favorite curse words:')
                    await ctx.message.channel.send('', file=discord.File(file_name, file_name))
                    os.remove(file_name)
                    await ctx.message.channel.send('What a potty mouth!')
                else:
                    await ctx.message.channel.send(f'Hmmm... {subject.name} doesn\'t seem to use bad language.')
        else:
            await ctx.message.channel.send(f'Usage: `df!dirtywordcloud User#0000`')

    @commands.command()
    async def countword(self, ctx, subject: discord.Member = None, word: str = None):
        """Counts the number of times a subject has used a word."""
        channel = ctx.message.channel

        if subject and word:
            data_id = await queries.get_latest_dataset(self.session, ctx, subject)
            if data_id:
                count = botutils.count_word(data_id, word)
                await channel.send(f"User {subject.name} has said {word} {count} times.")
