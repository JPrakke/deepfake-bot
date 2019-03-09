import os
import asyncio
from discord.ext import commands
import extract
import queries
import botutils
import plot_wordcloud

bot = commands.Bot(command_prefix='df!')


@bot.event
@asyncio.coroutine
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')
    queries.check_connection()


@bot.command(pass_context=True)
async def repeat(ctx, msg):
    """Prototype function for testing. Bot will repeat the message in the command."""
    print(msg)
    channel = ctx.message.channel
    await bot.send_message(channel, msg)


@bot.command(pass_context=True)
async def analyze(ctx, subject_string):
    """Extracts chat history of a subject if the user is registered"""

    queries.register_if_not_already(ctx)
    subject, error_message = botutils.get_subject(bot, ctx, subject_string, 'analyze')
    if subject:
        bot.loop.create_task(
            extract.extract_and_analyze(ctx, subject, bot)
        )
    else:
        await bot.send_message(ctx.message.channel, error_message)


@bot.command(pass_context=True)
async def wordcloud(ctx, subject_string):
    """Uploads a wordcloud image if a dataset exists for the mentioned subject"""

    queries.register_if_not_already(ctx)
    subject, error_message = botutils.get_subject(bot, ctx, subject_string, 'wordcloud')
    if subject:
        data_id = queries.get_latest_dataset(ctx, subject)
        if not data_id:
            await bot.send_message(ctx.message.channel,
                                   f'I can\'t find a data set for {subject_string}. Try: `df!analyze User#0000` first')
        else:
            plot_wordcloud.generate(data_id)
            await bot.send_message(ctx.message.channel, f'Here are {subject_string}\'s favorite words:')
            await bot.send_file(ctx.message.channel, f'../tmp/{data_id}-word-cloud.png')
            os.remove(f'../tmp/{data_id}-word-cloud.png')
    else:
        await bot.send_message(ctx.message.channel, error_message)


@bot.command(pass_context=True)
async def dirtywordcloud(ctx, subject_string):
    """Uploads a wordcloud image if a dataset exists for the mentioned subject"""

    queries.register_if_not_already(ctx)
    subject, error_message = botutils.get_subject(bot, ctx, subject_string, 'dirtywordcloud')
    if subject:
        data_id = queries.get_latest_dataset(ctx, subject)
        if not data_id:
            await bot.send_message(ctx.message.channel,
                                   f'I can\'t find a data set for {subject_string}. Try: `df!analyze User#0000` first')
        else:
            user_swears = plot_wordcloud.generate(data_id, True)
            if user_swears:
                await bot.send_message(ctx.message.channel, f'Here are {subject_string}\'s favorite curse words:')
                await bot.send_file(ctx.message.channel, f'../tmp/{data_id}-dirty-word-cloud.png')
                os.remove(f'../tmp/{data_id}-dirty-word-cloud.png')
                await bot.send_message(ctx.message.channel, 'What a potty mouth!')
            else:
                await bot.send_message(ctx.message.channel, f'Hmmm... {subject_string} doesn\'t use bad language.')
    else:
        await bot.send_message(ctx.message.channel, error_message)


@bot.command(pass_context=True)
async def train(ctx, user_mention):
    """Trains a model based on mentioned user. Must run analyze first."""
    channel = ctx.message.channel
    await bot.send_message(channel, "Not yet implemented...")


@bot.event
async def on_message(message):
    await bot.process_commands(message)


token = os.environ.get('DEEPFAKE_DISCORD_TOKEN')
bot.run(token)
