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
        connection_ok = self.parent_cog.cog_check(ctx)
        self.session = self.parent_cog.session
        return connection_ok

    @commands.command()
    async def wordcloud(self, ctx, *args):
        """Uploads a wordcloud image if a dataset exists for the mentioned subject"""

        if len(args) == 1:
            subject_string = args[0]
            filters = []
        elif len(args) == 2:
            subject_string = args[0]
            filters = args[1].split(',')
        else:
            await ctx.message.channel.send(
                               f'Use `wordcloud` to explore your subject\'s chat history and determine what words or '
                               + 'phrases should be filtered out of their model. These can be added as a list of comma '
                               + 'separated expressions in quotes.\n\n' +
                               f'Usage: `df!wordcloud <User#0000> <"filter1,filter2...">`\n' +
                               f'Without filters: `df!wordcloud <User#0000>`')
            return

        subject, error_message = botutils.get_subject(self.bot, ctx, subject_string, 'wordcloud')
        if subject:
            data_id = queries.get_latest_dataset(self.session, ctx, subject)
            if not data_id:
                await ctx.message.channel.send(
                      f'I can\'t find a data set for {subject_string}. Try: `df!analyze User#0000` first')
            else:
                file_name, n_messages, n_filtered = plot_wordcloud.generate(data_id, filters)
                await ctx.message.channel.send(f'Here are {subject_string}\'s favorite words:',
                                               file=discord.File(file_name, file_name))
                os.remove(file_name)
                await ctx.message.channel.send(f'Using {n_filtered} of {n_messages} messages.')
        else:
            await ctx.message.channel.send(error_message)

    @commands.command()
    async def activity(self, ctx, *args):
        """Uploads a time series and bar charts image if a dataset exists for the mentioned subject"""

        subject_string = args[0]
        subject, error_message = botutils.get_subject(self.bot, ctx, subject_string, 'activity')
        if subject:
            data_id = queries.get_latest_dataset(self.session, ctx, subject)
            if not data_id:
                await ctx.message.channel.send(
                      f'I can\'t find a data set for {subject_string[0]}. Try: `df!extract User#0000` first')
            else:
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
            await ctx.message.channel.send(error_message)

    @commands.command()
    async def dirtywordcloud(self, ctx, *args):
        """Uploads a wordcloud image of curse words if a dataset exists for the mentioned subject"""
        subject_string = args[0]
        subject, error_message = botutils.get_subject(self.bot, ctx, subject_string, 'dirtywordcloud')
        if subject:
            data_id = queries.get_latest_dataset(self.session, ctx, subject)
            if not data_id:
                await ctx.message.channel.send(
                                   f'I can\'t find a data set for {subject_string}. Try: `df!extract User#0000` first')
            else:
                file_name = plot_wordcloud.generate_dirty(data_id)
                if file_name:
                    await ctx.message.channel.send(f'Here are {subject_string}\'s favorite curse words:')
                    await ctx.message.channel.send('', file=discord.File(file_name, file_name))
                    os.remove(file_name)
                    await ctx.message.channel.send('What a potty mouth!')
                else:
                    await ctx.message.channel.send(f'Hmmm... {subject_string} doesn\'t seem to use bad language.')
        else:
            await ctx.message.channel.send(error_message)

    @commands.command()
    async def countword(self, ctx, *args):
        """Counts the number of times a subject has used a word."""
        channel = ctx.message.channel

        if len(args) is not 2:
            await ctx.message.channel.send('Usage: `df!countword <User#0000> <word>`')
            return

        subject_string = args[0]
        word = args[1]
        subject, _ = botutils.get_subject(self.bot, ctx, subject_string, '')
        if subject:
            data_id = queries.get_latest_dataset(self.session, ctx, subject)
            if not data_id:
                await ctx.message.channel.send(
                                   f'I can\'t find a data set for {subject_string}. Try: `df!extract User#0000` first')
            else:
                count = botutils.count_word(data_id, word)
                await channel.send(f"User {subject_string} has said {word} {count} times.")
