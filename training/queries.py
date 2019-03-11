import common.config
from common.tables import *
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
import datetime as dt


def start_job(data_uid):
    print('Connecting to database...')
    engine = create_engine(common.config.database_url)
    conn = engine.connect()
    session = Session(engine)

    data_set = session.query(DataSet)\
                      .filter(DataSet.data_uid == data_uid)\
                      .first()

    job = TrainingJob(
        data_id=data_set.id,
        time_started=dt.datetime.utcnow(),
        status="In progress"
    )

    job_id = job.id
    session.add(job)
    session.commit()
    session.close()
    engine.dispose()

    return job_id


def job_failed(job_id):
    engine = create_engine(common.config.database_url)
    conn = engine.connect()
    session = Session(engine)

    job = session.query(TrainingJob.filter(id == job_id)).first()
    job.time_finished = None
    job.status = "Failed"

    session.commit()
    session.close()
    engine.dispose()


def job_finished(job_id):
    engine = create_engine(common.config.database_url)
    conn = engine.connect()
    session = Session(engine)

    job = session.query(TrainingJob.filter(id == job_id)).first()
    job.time_finished = dt.datetime.utcnow()
    job.status = "Finished"

    session.commit()
    session.close()
    engine.dispose()
