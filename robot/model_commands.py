import discord
from discord.ext import commands
from robot import queries
import boto3
import json
import logging

logger = logging.getLogger(__name__)


class ModelCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.parent_cog = self.bot.get_cog('DeepFakeBot')
        self.session = self.parent_cog.session
        self.state_size = 3
        self.newline = False

    async def cog_check(self, ctx):
        connection_ok = await self.parent_cog.cog_check(ctx)
        self.session = self.parent_cog.session
        return connection_ok

    async def markovify_request(self, ctx, bot, subject_string, data_uid, filters, state_size, new_line):
        await bot.wait_until_ready()

        client = boto3.client('lambda', region_name='us-east-1')

        request_data = {
            "data_uid": data_uid,
            "filters": filters,
            "state_size": state_size,
            "new_line": new_line,
            "number_responses": 10
        }

        payload = json.dumps(request_data)

        response = client.invoke(
            FunctionName='deepfake-bot-markovify',
            InvocationType='RequestResponse',
            LogType='Tail',
            Payload=payload,
        )

        res_str = response['Payload'].read().decode('utf-8')
        res_json = json.loads(res_str)

        try:
            status_code = res_json['statusCode']
        except KeyError:
            status_code = 0

        if status_code == 200:
            sample_responses = res_json['body']
            model_uid = res_json['model_uid']

            await ctx.message.channel.send(
                f'Request complete!  model_uid: `{model_uid}`. Replying in the style of {subject_string}:'
            )

            for i in range(len(sample_responses)):
                res = f'**Message {i+1} of {len(sample_responses)}:**\n'
                res += f'```{sample_responses[i]}```\n'
                await ctx.message.channel.send(res)

            # Lambda function has already added the files to S3. Here we just add a record to the database.
            queries.create_markov_model(self.session, data_uid, model_uid)

        elif status_code == 0:
            # TODO: Write and link to 'Tips for Generating a Good Model'
            await ctx.message.channel.send(
                  'Markov chain generation failed. Make sure you have enough data and that it is properly filtered.'
            )
        else:
            logger.info('Markov generation failed...')
            logger.info(res_json)
            await ctx.message.channel.send(
                  'Hmm... I seem to be having some issues processing your `markovify` request. Maybe try again.'
            )

    @commands.group(name='markovify')
    async def markovify(self, ctx):
        """Markov chain generator commands"""
        pass

    @markovify.command()
    async def generate(self, ctx, *, subject: discord.Member):
        """Generates a markov chain model and sample responses in the style of your subject"""
        if subject:
            data_id = await queries.get_latest_dataset(self.session, ctx, subject)
            filters = queries.find_filters(self.session, ctx, subject)
            if data_id:
                await ctx.message.channel.send('Markovify request submitted...')
                self.bot.loop.create_task(
                    self.markovify_request(ctx, self.bot, subject.name, data_id, filters, self.state_size, self.newline)
                )
        else:
            await ctx.message.channel.send(f'Usage: `df!markovify User#0000`')

    @markovify.group(name='newline')
    async def newline(self, ctx):
        """Sets newline to on/off"""
        if ctx.invoked_subcommand is None:
            await ctx.send('Usage: `df!markovify newline <off/on>`')

    @newline.command()
    async def off(self, ctx):
        self.newline = False
        await ctx.send('markovify newline off')

    @newline.command()
    async def on(self, ctx):
        self.newline = True
        await ctx.send('markovify newline on')

    @markovify.command()
    async def state_size(self, ctx, new_value: int):
        """Changes the state size. Default value is 3. Smaller values tend to generate more chaotic sentences."""
        old_value = self.state_size
        self.state_size = new_value
        await ctx.send(f'Markovify state size changed from {old_value} to {new_value}')

    @markovify.command()
    async def settings(self, ctx):
        """Displays the current markovify settings."""
        await ctx.send(f'state size: {self.state_size}')
        await ctx.send(f'newline: {self.newline}')
