import common.config
from common.tables import *
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

# Setup connection
global conn, session
print('Connecting to database...')
engine = create_engine(common.config.database_url)
conn = engine.connect()
session = Session(engine)

# WIP....
def check_connection():
    result = session.query(Trainer).all()
    print(f'Connected... # of registered users: {len(result)}')

def check_if_registered(message):
    id_to_check = int(message.author.id)
    result = session.query(Trainer)\
        .filter(Trainer.discord_id==id_to_check)\
        .all()
    return len(result) != 0

def register_new_user(message, email):
    new_user = Trainer(
        discord_id=int(message.author.id),
        email=email,
        number_submitted_jobs=0,
        available_jobs=-1
    )
    session.add(new_user)
    session.commit()

def update_user_email(message, email):
    users_id = int(message.author.id)
    session.query(Trainer)\
        .filter(Trainer.discord_id==users_id)\
        .update({'email': email})
    session.commit()

def create_dataset(ctx, user_mention):
    return

def make_tables():
    sql = 'DROP TABLE IF EXISTS training_jobs, trainers, data_sets;'
    engine.execute(sql)
    Base.metadata.create_all(conn, checkfirst=False)

if __name__ == '__main__':
    make_tables()
    check_connection()