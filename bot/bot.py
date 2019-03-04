import os, random, asyncio
from discord.ext import commands
import extract, config

bot = commands.Bot(command_prefix="df!")

@bot.event
@asyncio.coroutine
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')

@bot.command(pass_context=True)
async def repeat(ctx, msg):
    """Prototype function for testing. Bot will repeat the message in the command."""
    print(msg)
    channel = ctx.message.channel
    await bot.send_message(channel, msg)

@bot.command(pass_context=True)
async def get_user_logs(ctx, user_mention):
    """Prototype function for testing. Print out the last 500 messages from the mentioned user."""
    bot.loop.create_task(
        extract.extract_user_chats(ctx, user_mention, bot)
    )

@bot.command(pass_context=True)
async def analyze(ctx, user_mention):
    """Extracts chat history for mentioned user. Performs analysis and ETL's into a flat text file for training."""
    #TODO: implent this
    channel = ctx.message.channel
    await bot.send_message(channel, "Not yet implimented...")

@bot.command(pass_context=True)
async def train(ctx, user_mention):
    """Trains a model based on mentioned user. Must run analyze first."""
    channel = ctx.message.channel
    await bot.send_message(channel, "Not yet implimented...")


token = os.environ.get('DEEPFAKE_DISCORD_TOKEN')
bot.run(token)