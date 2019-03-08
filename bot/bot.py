import os
import asyncio
from discord.ext import commands
from discord import utils
import extract
import queries

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

        try:
            subject_name = subject_string.split('#')[0]
            subject_discriminator = subject_string.split('#')[1]
            p = bot.get_all_members()
            found_members = filter(lambda m: (m.discriminator == subject_discriminator) \
                                         and (m.name == subject_name), p)

            subject = utils.get(found_members)

            bot.loop.create_task(
                extract.extract_and_analyze(ctx, subject, bot)
            )

        except IndexError:
            await bot.send_message(ctx.message.channel, f'{subject_string} doesn\'t seem to be a valid user. Usage: ```df!analyze user#0000```')

    else:
        await bot.send_message(ctx.message.channel, 'Hmmm... I can\'t seem to find you. Try ```df!register``` to get started.')

@bot.command(pass_context=True)
async def train(ctx, user_mention):
    """Trains a model based on mentioned user. Must run analyze first."""
    channel = ctx.message.channel
    await bot.send_message(channel, "Not yet implimented...")

@bot.command(pass_context=True)
async def register(ctx):
    await bot.send_message(ctx.message.channel, 'Direct message sent.')
    await bot.send_message(ctx.message.author, 'Reply to me with your email to get started.')

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