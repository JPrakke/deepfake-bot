import os, random, asyncio
from discord.ext import commands

bot = commands.Bot(command_prefix="dp!")

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
    channel = ctx.message.channel
    async for message in bot.logs_from(channel, limit=500):
        if message.author.mention == user_mention:
            print(message.content)

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


token = os.environ.get('DPPL_TOKEN')
bot.run(token)