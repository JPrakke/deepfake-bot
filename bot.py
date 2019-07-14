import os
from discord.ext import commands
from robot import extract
from robot import queries
from robot import botutils
from robot.db_connection import ConnectionManager
from robot.plot_commands import PlotCommands


class DeepFakeBot(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print('Logged in as')
        print(self.bot.user.name)
        print(self.bot.user.id)
        print('------')

    @commands.command(hidden=True)
    async def kill_app(self):
        connection_manager = self.bot.get_cog('ConnectionManager')
        if connection_manager is not None:
            connection_manager.close_db_connection()

        await self.bot.close()

    @commands.command()
    async def repeat(self, ctx, msg):
        """Prototype function for testing. Bot will repeat the message in the command."""
        print(msg)
        channel = ctx.message.channel
        await channel.send(msg)

    @commands.command()
    async def extract(self, ctx, *args):
        """Extracts chat history of a subject"""

        session = self.bot.get_cog('ConnectionManager').session
        queries.register_if_not_already(session, ctx)
        try:
            subject_string = args[0]
        except IndexError:
            await ctx.message.channel.send('Usage: `df!extract <User#0000>`')
            return

        subject, error_message = botutils.get_subject(self.bot, ctx, subject_string, 'extract')
        if subject:
            await ctx.message.channel.send(f'Extracting chat history for {subject.name}...')
            self.bot.loop.create_task(
                extract.extract_and_analyze(ctx, subject, self.bot)
            )
        else:
            await ctx.message.channel.send(error_message)

    @commands.command()
    async def reply_as(self, ctx, *args):
        session = self.bot.get_cog('ConnectionManager').session
        queries.register_if_not_already(session, ctx)
        subject_string = args[0]
        subject, error_message = botutils.get_subject(self.bot, ctx, subject_string, 'infer')
        if subject:
            data_uid, job_id = queries.get_latest_model(session, ctx, subject)
            if not job_id:
                await ctx.message.channel.send(f'Sorry, I can\'t find a model for {subject_string}')
            else:
                self.bot.loop.create_task(
                    botutils.infer(ctx, data_uid, job_id, self.bot)
                )


app = commands.Bot(command_prefix='df!')
app.add_cog(ConnectionManager(app))
app.add_cog(DeepFakeBot(app))
app.add_cog(PlotCommands(app))


@app.event
async def on_message(message):
    await app.process_commands(message)


def run_app():
    token = os.environ.get('DEEPFAKE_DISCORD_TOKEN')
    try:
        app.run(token)
    except RuntimeError as e:
        print('DeepfakeBot: Failed start attempt. I may have already been running.')
        print(e)


# Needed for the WSGI script in elastic beanstalk
class WSGIApp:
    def __call__(self, *args, **kwargs):
        run_app()


application = WSGIApp()

if __name__ == '__main__':
    run_app()
