from discord.ext import commands
from robot import queries
from robot import botutils
import boto3
import json


# TODO: update schema and store model records
class ModelCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.parent_cog = self.bot.get_cog('DeepFakeBot')
        self.session = self.parent_cog.session

    async def cog_check(self, ctx):
        connection_ok = await self.parent_cog.cog_check(ctx)
        self.session = self.parent_cog.session
        return connection_ok

    async def markovify_request(self, ctx, bot, subject_string, data_uid, filters, state_size, new_line):
        await bot.wait_until_ready()

        client = boto3.client('lambda', region_name='us-east-1')

        request_data = {
            "data_uid": data_uid,
            "filters": filters.split(','),
            "state_size": state_size,
            "new_line": new_line,
            "number_responses": 25
        }

        payload = json.dumps(request_data)
        print(payload)

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
            print(res_json)
            status_code = 0

        if status_code == 200:
            sample_responses = res_json['body']
            await ctx.message.channel.send(f'Replying in the style of {subject_string}:')
            for i in range(len(sample_responses)):
                res = f'`Message {i+1} of {len(sample_responses)}:`\n'
                res = f'{res}{sample_responses[i]}\n'
                await ctx.message.channel.send(res)
        elif status_code == 0:
            await ctx.message.channel.send(
                  'Sorry. I wasn\'t able to generate a valid Markov chain model. Try filtering your subject\'s data.'
            )
        else:
            await ctx.message.channel.send(
                  'Hmm... I seem to be having some issues processing your `markovify` request. Maybe try again.'
            )

    @commands.command()
    async def markovify(self, ctx, subject_string, state_size=3, new_line=False, filters=''):
        """Generates a markov chain model and sample responses in the style of your subject"""

        subject, error_message = botutils.get_subject(self.bot, ctx, subject_string, 'markofivy')

        if subject:
            data_id = queries.get_latest_dataset(self.session, ctx, subject)
            if not data_id:
                await ctx.message.channel.send(
                      f'I can\'t find a data set for {subject_string}. Try: `df!analyze User#0000` first')
            else:
                await ctx.message.channel.send('Markovify request submitted!')
                self.bot.loop.create_task(
                    self.markovify_request(ctx, self.bot, subject_string, data_id, filters, state_size, new_line)
                )
        else:
            await ctx.message.channel.send(error_message)
