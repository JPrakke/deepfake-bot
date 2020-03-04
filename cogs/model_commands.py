import discord
from discord.ext import commands
from cogs import db_queries
from cogs import config
from cogs import lambda_commands
import logging
import uuid
import os

logger = logging.getLogger(__name__)


class ModelCommands(lambda_commands.LambdaCommand):
    """Commands related to generating Markov chain models"""

    async def markovify_response(self, ctx, subject, model_uid):
        """What the bot should do if a Markov chain model is successfully generated"""

        # Open the file
        sample_response_file_name = f'./tmp/{model_uid}-sample-responses.txt'
        with open(sample_response_file_name, encoding='utf-8') as f:
            responses = f.read().split(config.unique_delimiter)

        # Respond
        await ctx.message.channel.send(
            f'Request complete!  model_uid: `{model_uid}`. Replying in the style of {subject.name}:'
        )

        for i in range(len(responses)):
            res = f'**Message {i + 1} of {len(responses)}:**\n'
            res += f'```{responses[i]}```\n'
            await ctx.message.channel.send(res)

        # Cleanup
        os.remove(sample_response_file_name)

    async def process_markovify(self, ctx, subject, data_uid, filters, state_size, new_line):
        model_uid = str(uuid.uuid4().hex)
        sample_response_file_name = f'{model_uid}-sample-responses.txt'

        request_data = {
            "data_uid": data_uid,
            "model_uid": model_uid,
            "filters": filters,
            "state_size": state_size,
            "new_line": new_line,
            "number_responses": 10
        }

        # Invoke the lambda function
        ok = await self.get_lambda_files(config.lambda_markov_name, request_data, [sample_response_file_name], 10,
                                         self.markovify_response, ctx, subject, model_uid)

        if not ok:
            # TODO: add link to documentation
            await ctx.send(f'Markov chain generator failed for {subject.name}.')
        else:
            db_queries.create_markov_model(self.parent_cog.session, data_uid, model_uid)

    @commands.group(name='markovify')
    async def markovify(self, ctx):
        """Markov chain generator commands"""
        pass

    @markovify.command()
    @commands.cooldown(5, 300, type=commands.BucketType.user)
    async def generate(self, ctx, *, subject: discord.Member):
        """Generates a markov chain model and sample responses in the style of your subject"""
        if subject:
            data_id = await db_queries.get_latest_dataset(self.session, ctx, subject)
            filters = db_queries.find_filters(self.session, ctx, subject)
            if data_id:
                state_size, newline = db_queries.get_markov_settings(self.session, ctx, subject)
                await ctx.send('Markovify request submitted...')
                await self.process_markovify(ctx, subject, data_id, filters, state_size, newline)
        else:
            await ctx.message.channel.send(f'Usage: `df!markovify <User#0000>`')

    @markovify.group(name='newline')
    @commands.cooldown(10, 60, type=commands.BucketType.user)
    async def newline(self, ctx):
        """Sets newline to on/off"""
        if ctx.invoked_subcommand is None:
            await ctx.send('Usage: `df!markovify newline <off/on> <User#0000>`')

    @newline.command()
    @commands.cooldown(10, 60, type=commands.BucketType.user)
    async def off(self, ctx, *, subject: discord.Member):
        if subject:
            state_size, _ = db_queries.get_markov_settings(self.session, ctx, subject)
            db_queries.update_markov_settings(self.session, ctx, subject, state_size, False)
            await ctx.send(f'markovify newline off for user {subject.name}')
        else:
            await ctx.send('Usage: `df!markovify newline off <User#0000>`')

    @newline.command()
    @commands.cooldown(10, 60, type=commands.BucketType.user)
    async def on(self, ctx, *, subject: discord.Member):
        if subject:
            state_size, _ = db_queries.get_markov_settings(self.session, ctx, subject)
            db_queries.update_markov_settings(self.session, ctx, subject, state_size, True)
            await ctx.send(f'markovify newline on for user {subject.name}')
        else:
            await ctx.send('Usage: `df!markovify newline on <User#0000>`')

    @markovify.command()
    @commands.cooldown(10, 60, type=commands.BucketType.user)
    async def state_size(self, ctx, subject: discord.Member, new_value: int):
        """Changes the state size. Default value is 3. Smaller values tend to generate more chaotic sentences."""
        old_value, newline = db_queries.get_markov_settings(self.session, ctx, subject)
        db_queries.update_markov_settings(self.session, ctx, subject, new_value, newline)
        await ctx.send(f'Markovify state size changed from {old_value} to {new_value} for {subject.name}')

    @markovify.command()
    @commands.cooldown(10, 60, type=commands.BucketType.user)
    async def settings(self, ctx, *, subject: discord.Member):
        """Displays the current markovify settings."""
        if subject:
            state_size, newline = db_queries.get_markov_settings(self.session, ctx, subject)
            await ctx.send(f'state size: {state_size}')
            await ctx.send(f'newline: {newline}')
        else:
            await ctx.send('Usage: `df!markovify settings <User#0000>`')
