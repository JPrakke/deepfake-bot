import os
import asyncio
from discord.ext import commands
from bot import extract
from bot import queries
from bot import botutils
from bot import plot_wordcloud
from bot import plot_activity

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
async def analyze(ctx, *args):
    """Extracts chat history of a subject if the user is registered"""

    queries.register_if_not_already(ctx)
    subject_string = args[0]
    subject, error_message = botutils.get_subject(bot, ctx, subject_string, 'analyze')
    if subject:
        await bot.send_message(ctx.message.channel, f'Analyzing {subject.name}...')
        bot.loop.create_task(
            extract.extract_and_analyze(ctx, subject, bot)
        )
    else:
        await bot.send_message(ctx.message.channel, error_message)


@bot.command(pass_context=True)
async def wordcloud(ctx, *args):
    """Uploads a wordcloud image if a dataset exists for the mentioned subject"""

    queries.register_if_not_already(ctx)

    if len(args) == 1:
        subject_string = args[0]
        filters = []
    elif len(args) == 2:
        subject_string = args[0]
        filters = args[1].split(',')
    else:
        await bot.send_message(ctx.message.channel,
                               f'Use `wordcloud` to explore your subject\'s chat history and determine what words or '
                               + 'phrases should be filtered out of your model. These can be added as a list of comma '
                               + 'separated expressions in quotes.\n\n' +
                               f'With filters: `df!wordcloud <User#0000> <"filter1,filter2...">`\n' +
                               f'Without filters: `df!wordcloud <User#0000>`')
        return

    subject, error_message = botutils.get_subject(bot, ctx, subject_string, 'wordcloud')
    if subject:
        data_id = queries.get_latest_dataset(ctx, subject)
        if not data_id:
            await bot.send_message(ctx.message.channel,
                                   f'I can\'t find a data set for {subject_string}. Try: `df!analyze User#0000` first')
        else:
            file_name, n_messages, n_filtered = plot_wordcloud.generate(data_id, filters)
            await bot.send_message(ctx.message.channel, f'Here are {subject_string}\'s favorite words:')
            await bot.send_file(ctx.message.channel, file_name)
            os.remove(file_name)
            await bot.send_message(ctx.message.channel, f'Using {n_filtered} of {n_messages} messages.')
    else:
        await bot.send_message(ctx.message.channel, error_message)


@bot.command(pass_context=True)
async def activity(ctx, *args):
    """Uploads a time series and bar charts image if a dataset exists for the mentioned subject"""

    queries.register_if_not_already(ctx)
    subject_string = args[0]
    subject, error_message = botutils.get_subject(bot, ctx, subject_string, 'activity')
    if subject:
        data_id = queries.get_latest_dataset(ctx, subject)
        if not data_id:
            await bot.send_message(ctx.message.channel,
                                   f'I can\'t find a data set for {subject_string[0]}. Try: `df!analyze User#0000` first')
        else:
            file_name = plot_activity.generate(data_id, subject.name)
            await bot.send_file(ctx.message.channel, file_name)
            os.remove(file_name)

            bar_file_name, bar_file_name_log = plot_activity.bar_charts(data_id, subject.name)

            # Only make bar charts if more than one channel
            if bar_file_name and bar_file_name_log:
                await bot.send_file(ctx.message.channel, bar_file_name)
                await bot.send_file(ctx.message.channel, bar_file_name_log)
                os.remove(bar_file_name)
                os.remove(bar_file_name_log)
                await bot.send_message(ctx.message.channel,
                                   """Don\'t see a channel? Make sure I have permission to read 
it before running `df!analyze`.""")

    else:
        await bot.send_message(ctx.message.channel, error_message)


@bot.command(pass_context=True)
async def dirtywordcloud(ctx, *args):
    """Uploads a wordcloud image of curse words if a dataset exists for the mentioned subject"""

    queries.register_if_not_already(ctx)
    subject_string = args[0]
    subject, error_message = botutils.get_subject(bot, ctx, subject_string, 'dirtywordcloud')
    if subject:
        data_id = queries.get_latest_dataset(ctx, subject)
        if not data_id:
            await bot.send_message(ctx.message.channel,
                                   f'I can\'t find a data set for {subject_string}. Try: `df!analyze User#0000` first')
        else:
            file_name = plot_wordcloud.generate_dirty(data_id)
            if file_name:
                await bot.send_message(ctx.message.channel, f'Here are {subject_string}\'s favorite curse words:')
                await bot.send_file(ctx.message.channel, file_name)
                os.remove(file_name)
                await bot.send_message(ctx.message.channel, 'What a potty mouth!')
            else:
                await bot.send_message(ctx.message.channel, f'Hmmm... {subject_string} doesn\'t use bad language.')
    else:
        await bot.send_message(ctx.message.channel, error_message)


@bot.command(pass_context=True)
async def countword(ctx, *args):
    """Counts the number of times a subject has used a word."""
    channel = ctx.message.channel
    queries.register_if_not_already(ctx)

    if len(args) is not 2:
        await bot.send_message(ctx.message.channel, 'Usage: `df!wordcount <User#0000> <word>`')
        return

    subject_string = args[0]
    word = args[1]
    subject, _ = botutils.get_subject(bot, ctx, subject_string, '')
    data_id = queries.get_latest_dataset(ctx, subject)

    count = botutils.count_word(data_id, word)
    await bot.send_message(channel, f"User {subject_string} has said {word} {count} times.")


@bot.command(pass_context=True)
async def reply_as(ctx, *args):
    queries.register_if_not_already(ctx)
    subject_string = args[0]
    subject, error_message = botutils.get_subject(bot, ctx, subject_string, 'infer')
    if subject:
        data_uid, job_id = queries.get_latest_model(ctx, subject)
        if not job_id:
            await bot.send_message(ctx.message.channel, f'Sorry, I can\'t find a model for {subject_string}')
        else:
            bot.loop.create_task(
                botutils.infer(ctx, data_uid, job_id, bot)
            )


@bot.command(pass_context=True)
async def train(ctx, *args):
    """Trains a model based on mentioned user. Must run analyze first."""
    channel = ctx.message.channel
    await bot.send_message(channel, "Not yet implemented...")


@bot.event
async def on_message(message):
    await bot.process_commands(message)


# Needed for the WSGI script in elastic beanstalk
class WSGIApp:
    def __call__(self, *args, **kwargs):
        # Because I'm curious what WSGI is doing. TODO: remove this later.
        print(args)
        print(kwargs)
        token = os.environ.get('DEEPFAKE_DISCORD_TOKEN')
        bot.run(token)


global application
application = WSGIApp()

if __name__ == '__main__':
    application()
