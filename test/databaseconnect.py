import unittest
import cogs.config
from cogs.db_schema import *
from sqlalchemy import create_engine
from sqlalchemy.orm import Session


class DatabaseTests(unittest.TestCase):
    def setup_connection(self):
        print('Connecting to database...')
        self.engine = create_engine(cogs.config.database_url)
        self.conn = self.engine.connect()
        self.session = Session(self.engine)

    def close_connection(self):
        print('Closing connection...')
        self.conn.close()
        self.session.close()
        self.engine.dispose()

    def test_user_count(self):
        self.setup_connection()

        number_of_users = len(self.session.query(Trainer).all())
        self.assertGreater(number_of_users, 0)

        self.close_connection()

    def test_bad_filter(self):
        bad_filter = '@🅟🅞🅟~'

        self.setup_connection()
        self.session.query(Trainer).filter(Trainer.user_name == bad_filter).all()
        self.close_connection()


if __name__ == '__main__':
    unittest.main()
