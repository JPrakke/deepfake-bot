from discord.ext import commands
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
import sqlalchemy.ext
from robot.config import *
import robot.queries


class DeepFakeBotConnectionError(Exception):
    pass


class ConnectionManager(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.engine = None
        self.conn = None
        self.session = None
        self.create_connection()

    def create_connection(self):
        print('Connecting to database...')
        self.engine = create_engine(database_url, pool_pre_ping=True)
        self.conn = self.engine.connect()
        self.session = Session(self.engine)
        robot.queries.check_connection(self.session)

    def close_db_connection(self):
        self.conn.close()
        self.session.close()
        self.engine.dispose()
        print('Connection closed...')

    def refresh_connection(self):
        try:
            robot.queries.ping_connection(self.session)
        except sqlalchemy.exc.OperationalError:
            print('SQL issue. Re-establishing the connection...')
            try:
                self.close_db_connection()
                self.create_connection()
                robot.queries.ping_connection(self.session)
            except Exception:
                raise DeepFakeBotConnectionError('Problem reconnecting to database...')
