import unittest
import cogs.config
from cogs.db_schema import *
from sqlalchemy import create_engine
from sqlalchemy.orm import Session


class DatabaseTests(unittest.TestCase):
    def test_user_count(self):
        print('Connecting to database...')
        engine = create_engine(cogs.config.database_url)
        conn = engine.connect()
        session = Session(engine)

        number_of_users = len(session.query(Trainer).all())

        conn.close()
        session.close()
        engine.dispose()

        self.assertGreater(number_of_users, 0)


if __name__ == '__main__':
    unittest.main()
