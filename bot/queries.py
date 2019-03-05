import common.config
import common.tables
from sqlalchemy import create_engine

# Make this global so we can reuse the connection for each query
global conn
print('Connecting to database...')
engine = create_engine(common.config.database_url)
conn = engine.connect()

# WIP....
def query1():
    table_names = common.tables.Base.metadata.tables.keys()
    print('Connected... database tables:')
    for t in table_names:
        print(t)

def register_user(ctx):
    return

def create_dataset(ctx, user_mention):
    return

def make_tables():
    common.tables.Base.metadata.drop_all(conn, checkfirst=False)
    common.tables.Base.metadata.create_all(conn, checkfirst=False)

if __name__ == '__main__':
    make_tables()