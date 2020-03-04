import os
import logging
import math
from discord.ext import commands
from cogs.db_connection import ConnectionManager
from cogs.core_commands import CoreCommands
from cogs.filter_commands import FilterCommands
from cogs.plot_commands import PlotCommands
from cogs.model_commands import ModelCommands
from cogs.deploy_commands import DeployCommands

logger = logging.getLogger(__name__)


class DeepFakeBot(commands.Bot):
    async def on_command_error(self, ctx, exception):
        if isinstance(exception, commands.CommandOnCooldown):
            await ctx.send(f'Whoa, {ctx.author.name} slow down there! '
                           f'Try using `{ctx.invoked_with}` again in {math.ceil(exception.retry_after)}s')


def run_app():
    app = DeepFakeBot(command_prefix='df!')
    app.add_cog(ConnectionManager(app))
    app.add_cog(CoreCommands(app))
    app.add_cog(FilterCommands(app))
    app.add_cog(PlotCommands(app))
    app.add_cog(ModelCommands(app))
    app.add_cog(DeployCommands(app))

    @app.event
    async def on_message(message):
        await app.process_commands(message)

    token = os.environ.get('DEEPFAKE_DISCORD_TOKEN')
    try:
        app.run(token)
    except RuntimeError as e:
        logger.error('DeepfakeBot: Failed start attempt. I may have already been running.')
        logger.error(e)


if __name__ == '__main__':
    logging.basicConfig(
        format='%(asctime)s %(levelname)-8s %(message)s',
        level=logging.INFO,
        datefmt='%Y-%m-%d %H:%M:%S')
    run_app()
