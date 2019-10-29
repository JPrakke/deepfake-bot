import discord
from discord.ext import commands
from cogs import db_queries
from cogs import plot_wordcloud
from cogs import plot_activity
import s3fs
import gzip
from cogs.config import *


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
        """Uploads a wordcloud image if a data set exists for the mentioned subject"""
        if subject:
            data_id = await db_queries.get_latest_dataset(self.session, ctx, subject)
            if data_id:
                filters = db_queries.find_filters(self.session, ctx, subject)
                file_name, n_messages, n_filtered = plot_wordcloud.generate(data_id, filters)
                await ctx.message.channel.send(f'Here are {subject.name}\'s favorite words:',
                                               file=discord.File(file_name, file_name))
                os.remove(file_name)
                await ctx.message.channel.send(f'Using {n_filtered} of {n_messages} messages.')
        else:
            await ctx.message.channel.send(f'Usage: `df!wordcloud User#0000`')

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
    async def dirtywordcloud(self, ctx, *, subject: discord.Member):
        """Uploads a wordcloud image of curse words if a dataset has been extracted for the mentioned subject"""
        if subject:
            data_id = await db_queries.get_latest_dataset(self.session, ctx, subject)
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
        if subject and word:
            data_id = await db_queries.get_latest_dataset(self.session, ctx, subject)
            if data_id:
                # Read the file from S3
                s3 = s3fs.S3FileSystem(key=aws_access_key_id,
                                       secret=aws_secret_access_key)
                with s3.open(f'{aws_s3_bucket_prefix}/{data_id}-text.dsv.gz', mode='rb') as f:
                    g = gzip.GzipFile(fileobj=f)
                    content = g.read().decode().replace(unique_delimiter, ' ')

                # Regex for the word in question
                expr = f'[ ]{word.lower()}[.!? ]'
                reg = re.compile(expr)
                count = len(reg.findall(content.lower()))

                await ctx.message.channel.send(f"User {subject.name} has said {word} {count} times.")
