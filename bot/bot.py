import os
import asyncio
from discord.ext import commands
from discord import utils
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

    is_registered = queries.check_if_registered(ctx.message)

    if is_registered:
        subject = botutils.get_subject(bot, ctx, subject_string)

        if subject == 'Too many...':
            await bot.send_message(ctx.message.channel,
                                   f'One at a time please. Usage: `df!analyze User#0000`')
        elif subject == 'Not found':
            await bot.send_message(ctx.message.channel,
                                   f'{subject_string} doesn\'t seem to be a valid user. Usage: `df!analyze User#0000`')
        else:
            bot.loop.create_task(
                extract.extract_and_analyze(ctx, subject, bot)
            )

    else:
        await bot.send_message(ctx.message.channel,
                               'Hmmm... I can\'t seem to find you. Try `df!register` to get started.')


@bot.command(pass_context=True)
async def wordcloud(ctx, subject_string):
    """Uploads a wordcloud image if a dataset exists for the mentioned subject"""

    is_registered = queries.check_if_registered(ctx.message)

    if is_registered:
        subject = botutils.get_subject(bot, ctx, subject_string)

        if subject == 'Too many...':
            await bot.send_message(ctx.message.channel,
                                   f'One at a time please. Usage: `df!analyze User#0000`')
        elif subject == 'Not found':
            await bot.send_message(ctx.message.channel,
                                   f'{subject_string} doesn\'t seem to be a valid user. Usage: `df!analyze User#0000`')
        else:
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
        await bot.send_message(ctx.message.channel,
                               'Hmmm... I can\'t seem to find you. Try `df!register` to get started.')


@bot.command(pass_context=True)
async def dirtywordcloud(ctx, subject_string):
    """Uploads a wordcloud image if a dataset exists for the mentioned subject"""

    is_registered = queries.check_if_registered(ctx.message)

    if is_registered:
        subject = botutils.get_subject(bot, ctx, subject_string)

        if subject == 'Too many...':
            await bot.send_message(ctx.message.channel,
                                   f'One at a time please. Usage: `df!analyze User#0000`')
        elif subject == 'Not found':
            await bot.send_message(ctx.message.channel,
                                   f'{subject_string} doesn\'t seem to be a valid user. Usage: `df!analyze User#0000`')
        else:
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
        await bot.send_message(ctx.message.channel,
                               'Hmmm... I can\'t seem to find you. Try `df!register` to get started.')


@bot.command(pass_context=True)
async def train(ctx, user_mention):
    """Trains a model based on mentioned user. Must run analyze first."""
    channel = ctx.message.channel
    await bot.send_message(channel, "Not yet implemented...")


@bot.command(pass_context=True)
async def register(ctx):
    await bot.send_message(ctx.message.channel, 'Direct message sent.')
    await bot.send_message(ctx.message.author,
                           'Reply to me with your email to get started. (Feel free to make one up! e.g. me@mail.mail)')


@bot.event
async def on_message(message):
    if message.server is None and message.author != bot.user:
        email = message.content
        if '@' in email:
            if queries.check_if_registered(message):
                queries.update_user_email(message, email)
                await bot.send_message(message.author, 'Email updated.')
            else:
                queries.register_new_user(message, email)
                await bot.send_message(message.author, 'Registered!')
        else:
            await bot.send_message(message.author, 'That doesn\'t seem to be a valid email.')

    await bot.process_commands(message)


token = os.environ.get('DEEPFAKE_DISCORD_TOKEN')
bot.run(token)
