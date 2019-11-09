import discord
from discord.ext import commands
from cogs import db_queries
from cogs import config
from cogs import lambda_commands
import logging

logger = logging.getLogger(__name__)


async def process_markovify_request(bot, ctx, subject_string, data_uid, filters, state_size, new_line):
    #await bot.wait_until_ready()

    request_data = {
        "data_uid": data_uid,
        "filters": filters,
        "state_size": state_size,
        "new_line": new_line,
        "number_responses": 10
    }

    # Invoke the lambda function
    lambda_cog = bot.get_cog('ModelCommands')
    res_json = await lambda_cog.invoke_lambda(ctx, config.lambda_markov_name, request_data, 'Markovify')

    if res_json:
        sample_responses = res_json['body']
        model_uid = res_json['model_uid']

        await ctx.message.channel.send(
            f'Request complete!  model_uid: `{model_uid}`. Replying in the style of {subject_string}:'
        )

        for i in range(len(sample_responses)):
            res = f'**Message {i + 1} of {len(sample_responses)}:**\n'
            res += f'```{sample_responses[i]}```\n'
            await ctx.message.channel.send(res)

        # Lambda function has already added the files to S3. Here we just add a record to the database.
        db_queries.create_markov_model(lambda_cog.session, data_uid, model_uid)

    else:
        # TODO: Write and link to 'Tips for Generating a Good Model'
        await ctx.message.channel.send(
            'Markov chain generation failed. Make sure you have enough data and that it is properly filtered.'
        )


class ModelCommands(lambda_commands.LambdaCommand):

    @commands.group(name='markovify')
    async def markovify(self, ctx):
        """Markov chain generator commands"""
        pass

    @markovify.command()
    async def generate(self, ctx, *, subject: discord.Member):
        """Generates a markov chain model and sample responses in the style of your subject"""
        if subject:
            data_id = await db_queries.get_latest_dataset(self.session, ctx, subject)
            filters = db_queries.find_filters(self.session, ctx, subject)
            if data_id:
                state_size, newline = db_queries.get_markov_settings(self.session, ctx, subject)
                await ctx.send('Markovify request submitted...')
                self.bot.loop.create_task(
                    process_markovify_request(self.bot, ctx, subject.name, data_id, filters, state_size, newline)
                )
        else:
            await ctx.message.channel.send(f'Usage: `df!markovify User#0000`')

    @markovify.group(name='newline')
    async def newline(self, ctx):
        """Sets newline to on/off"""
        if ctx.invoked_subcommand is None:
            await ctx.send('Usage: `df!markovify newline <off/on> User#0000`')

    @newline.command()
    async def off(self, ctx, *, subject: discord.Member):
        if subject:
            state_size, _ = db_queries.get_markov_settings(self.session, ctx, subject)
            db_queries.update_markov_settings(self.session, ctx, subject, state_size, False)
            await ctx.send(f'markovify newline off for user {subject.name}')
        else:
            await ctx.send('Usage: `df!markovify newline off @User#0000`')

    @newline.command()
    async def on(self, ctx, *, subject: discord.Member):
        if subject:
            state_size, _ = db_queries.get_markov_settings(self.session, ctx, subject)
            db_queries.update_markov_settings(self.session, ctx, subject, state_size, True)
            await ctx.send(f'markovify newline on for user {subject.name}')
        else:
            await ctx.send('Usage: `df!markovify newline on @User#0000`')

    @markovify.command()
    async def state_size(self, ctx, subject: discord.Member, new_value: int):
        """Changes the state size. Default value is 3. Smaller values tend to generate more chaotic sentences."""
        old_value, newline = db_queries.get_markov_settings(self.session, ctx, subject)
        db_queries.update_markov_settings(self.session, ctx, subject, new_value, newline)
        await ctx.send(f'Markovify state size changed from {old_value} to {new_value} for {subject.name}')

    @markovify.command()
    async def settings(self, ctx, *, subject: discord.Member):
        """Displays the current markovify settings."""
        if subject:
            state_size, newline = db_queries.get_markov_settings(self.session, ctx, subject)
            await ctx.send(f'state size: {state_size}')
            await ctx.send(f'newline: {newline}')
        else:
            await ctx.send('Usage: `df!markovify settings @User#0000`')
