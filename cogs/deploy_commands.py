import discord
from discord.ext import commands
from cogs import db_queries
import cogs.config
import s3fs
from cryptography.fernet import Fernet
import os
import json
import logging

logger = logging.getLogger(__name__)


class DeployCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.parent_cog = self.bot.get_cog('CoreCommands')
        self.session = self.parent_cog.session
        self.s3 = s3fs.S3FileSystem(key=cogs.config.aws_access_key_id,
                                    secret=cogs.config.aws_secret_access_key)

    async def cog_check(self, ctx):
        connection_ok = await self.parent_cog.cog_check(ctx)
        self.session = self.parent_cog.session
        return connection_ok

    def download_and_encrypt(self, model_uid):
        # Read from S3
        model_file_name = f'{model_uid}-markov-model.json.gz'
        encrypted_file_name = model_file_name.replace('markov-model', 'markov-model-encrypted')
        with self.s3.open(f'{cogs.config.aws_s3_bucket_prefix}/{model_file_name}', mode='rb') as f:
            content = f.read()

        # Generate encryption key
        key = Fernet.generate_key()
        fer = Fernet(key)
        encrypted = fer.encrypt(content)

        # Add encrypted model to temporary space
        with open(f'./tmp/{encrypted_file_name}', mode='wb') as f:
            f.write(encrypted)

        return key, encrypted_file_name

    @commands.group(name='deploy')
    async def deploy(self, ctx):
        """Deploy commands"""
        pass

    @deploy.command()
    @commands.cooldown(10, 300, type=commands.BucketType.user)
    async def self(self, ctx, *, subject: discord.Member):
        model_uid = await db_queries.get_latest_markov_model(self.session, ctx, subject)
        if model_uid:

            # Create and record an encrypted model
            key, encrypted_file_name = self.download_and_encrypt(model_uid)
            db_queries.create_deployment(self.session, ctx, model_uid, key.decode())

            # Create a config file with default settings
            default_settings = {'reply_probability': 0.3,
                                'new_conversation_min_wait': 60,
                                'new_conversation_max_wait': 3600,
                                'max_sentence_length': 500,
                                'max_markov_chains': 100,
                                'selection_algorithm': 'cosine_similarity',
                                'quiet_mode': False,
                                'avg_delay': 2,
                                'std_dev_delay': 2,
                                'min_delay': 0.5,
                                'avg_typing_speed': 60,
                                'std_dev_typing_speed': 10,
                                'min_typing_speed': 40,
                                'white_list_server_ids': [ctx.message.guild.id],
                                'owner_id': ctx.message.author.id,
                                'bot_prefix': 'df?',
                                'version': cogs.config.version
                                }

            config_file_name = f'{model_uid}-config.json'
            with open(f'./tmp/{config_file_name}', 'w') as f:
                f.write(json.dumps(default_settings, indent=4, separators=(',', ': ')))

            # Message the files
            await ctx.send(f'Here are the model artifacts for {subject.name}\'s bot:',
                           files=[discord.File(f'./tmp/{encrypted_file_name}'),
                                  discord.File(f'./tmp/{config_file_name}')])
            await ctx.message.author.send(f'Your secret key for {subject.name}\'s bot: `{key.decode()}`')
            await ctx.message.author.send(f'{subject.name}\'s avatar can be downloaded from: {subject.avatar_url_as()}')

            # Cleanup disk
            os.remove(f'./tmp/{encrypted_file_name}')
            os.remove(f'./tmp/{config_file_name}')

    @deploy.command()
    async def hosted(self, ctx):
        await ctx.send('Not yet implemented...')
