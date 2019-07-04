import json, uuid, gzip, boto3, os
import datetime as dt
import asyncio
import discord

bot = discord.Client()


@bot.event
@asyncio.coroutine
async def on_ready():
    print('Lambda function extract logged in as:')
    print(bot.user.name)
    print(bot.user.id)
    print('------')
    await bot.logout()


def lambda_handler(event, context):
    token = os.environ.get('DEEPFAKE_DISCORD_TOKEN')
    bot.run(token)
    bot.close()
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }


if __name__ == '__main__':
    a = lambda_handler(None, None)
    print(a)
