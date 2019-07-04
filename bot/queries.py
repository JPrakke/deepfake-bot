import common.config
from common.tables import *
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy import func
import datetime as dt

# Setup connection
global conn, session
print('Connecting to database...')
engine = create_engine(common.config.database_url)
conn = engine.connect()
session = Session(engine)

# Keep the connection open in case the bot is idle
engine.execute('SET SESSION wait_timeout=31536000')


# WIP....
def check_connection():
    result = session.query(Trainer).all()
    print(f'Connected... # of registered users: {len(result)}')


def register_if_not_already(ctx):
    id_to_check = int(ctx.message.author.id)
    result = session.query(Trainer) \
        .filter(Trainer.discord_id == id_to_check) \
        .all()

    if len(result) == 0:
        new_user = Trainer(
            discord_id=int(ctx.message.author.id),
            user_name=f'{ctx.message.author.name}#{ctx.message.author.discriminator}',
            number_submitted_jobs=0,
            available_jobs=-1
        )
        session.add(new_user)
        session.commit()


def create_dataset(ctx, user_mention, uid):
    new_dataset = DataSet(
        trainer_id=int(ctx.message.author.id),
        subject_id=int(user_mention.id),
        server_name=ctx.message.server.name,
        server_id=int(ctx.message.server.id),
        time_collected=dt.datetime.utcnow(),
        data_uid=uid
    )
    session.add(new_dataset)
    session.commit()


def get_latest_dataset(ctx, user_mention):
    result = session.query(DataSet)\
        .filter(DataSet.subject_id == int(user_mention.id))\
        .filter(DataSet.server_id == int(ctx.message.server.id))\
        .all()

    max_ts = dt.datetime.min
    for r in result:
        if r.time_collected > max_ts:
            max_ts = r.time_collected
            uid = r.data_uid

    if max_ts is not dt.datetime.min:
        return uid
    else:
        return False


def get_latest_model(ctx, user_mention):
    """Returns a data_uid and job_ib from the latest finished training job"""""
    latest_finished_job = session.query(TrainingJob) \
                                 .join(DataSet) \
                                 .filter(DataSet.subject_id == user_mention.id) \
                                 .filter(DataSet.server_id == ctx.message.server.id) \
                                 .filter(TrainingJob.status == 'Finished') \
                                 .order_by(TrainingJob.id.desc()) \
                                 .first()

    if latest_finished_job is not None:
        data_id = session.query(DataSet.data_uid)\
                         .join(TrainingJob)\
                         .filter(TrainingJob.id == latest_finished_job.id)\
                         .first()\
                         .data_uid
        return data_id, latest_finished_job.id
    else:
        return False, False


def make_tables():
    sql = 'DROP TABLE IF EXISTS training_jobs, trainers, data_sets;'
    engine.execute(sql)
    Base.metadata.create_all(conn, checkfirst=False)


if __name__ == '__main__':
    make_tables()
    check_connection()
