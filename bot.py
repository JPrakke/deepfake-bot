import os
import logging
import discord
from discord.ext import commands
from robot import extract
from robot import queries
from robot.db_connection import ConnectionManager
from robot.db_connection import DeepFakeBotConnectionError
from robot.filter_commands import FilterCommands
from robot.plot_commands import PlotCommands
from robot.model_commands import ModelCommands
from robot.deploy_commands import DeployCommands

logger = logging.getLogger(__name__)


class DeepFakeBot(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.session = None

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
        queries.register_trainer(self.session, ctx)
        return True

    @commands.Cog.listener()
    async def on_ready(self):
        logger.info('Logged in as')
        logger.info(self.bot.user.name)
        logger.info(self.bot.user.id)
        logger.info('------')

    @commands.command()
    async def repeat(self, ctx, msg):
        """Function for testing. Bot will repeat the message in the command."""
        logger.info(msg)
        channel = ctx.message.channel
        await channel.send(msg)

    @commands.command()
    async def extract(self, ctx, *, subject: discord.Member = None):
        """Extracts chat history of a subject"""
        if subject:
            queries.register_subject(self.session, ctx, subject)
            await ctx.message.channel.send(
                  f'Extracting chat history for {subject.name}... (This could take a few minutes).'
            )
            self.bot.loop.create_task(
                extract.extract_chat_history(ctx, subject, self.bot)
            )
        else:
            await ctx.message.channel.send("'Usage: `df!extract <User#0000>`'")


app = commands.Bot(command_prefix='df!')
app.add_cog(ConnectionManager(app))
app.add_cog(DeepFakeBot(app))
app.add_cog(FilterCommands(app))
app.add_cog(PlotCommands(app))
app.add_cog(ModelCommands(app))
app.add_cog(DeployCommands(app))


@app.event
async def on_message(message):
    await app.process_commands(message)


def run_app():
    token = os.environ.get('DEEPFAKE_DISCORD_TOKEN')
    try:
        app.run(token)
    except RuntimeError as e:
        logger.error('DeepfakeBot: Failed start attempt. I may have already been running.')
        logger.error(e)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    run_app()
