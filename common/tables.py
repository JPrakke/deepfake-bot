from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, BigInteger, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship

Base = declarative_base()


class Trainer(Base):
    __tablename__ = 'trainers'
    id = Column(Integer, primary_key=True)
    discord_id = Column(BigInteger, unique=True)
    user_name = Column(String(255))
    email = Column(String(255))
    number_submitted_jobs = Column(Integer)
    available_jobs = Column(Integer)


class DataSet(Base):
    __tablename__ = 'data_sets'
    id = Column(Integer, primary_key=True)
    trainer_id = Column(BigInteger, ForeignKey('trainers.discord_id'))
    subject_id = Column(BigInteger)
    server_id = Column(BigInteger)
    server_name = Column(String(255))
    time_collected = Column(DateTime)
    data_uid = Column(String(32), unique=True)
    trainer_discord_id = relationship('Trainer', foreign_keys=[trainer_id])


class TrainingJob(Base):
    __tablename__ = 'training_jobs'
    id = Column(Integer, primary_key=True)
    data_id = Column(Integer, ForeignKey('data_sets.id'))
    time_started = Column(DateTime)
    time_finished = Column(DateTime)
    status = Column(String(16))  # 'In progress', 'Failed', or 'Finished'
    data_set_id = relationship('DataSet', foreign_keys=[data_id])
