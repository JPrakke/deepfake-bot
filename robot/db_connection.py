from discord.ext import commands
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from robot.config import *
import robot.queries


class ConnectionManager(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        print('Connecting to database...')
        self.connection = None
        self.engine = create_engine(database_url, pool_pre_ping=True)
        self.conn = self.engine.connect()
        self.session = Session(self.engine)
        robot.queries.check_connection(self.session)
