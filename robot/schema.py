from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, BigInteger, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship

Base = declarative_base()


class Trainer(Base):
    """Bot users"""
    __tablename__ = 'trainers'
    id = Column(BigInteger, primary_key=True)
    discord_id = Column(BigInteger, unique=True)
    user_name = Column(String(255))
    time_registered = Column(Integer)


class Subject(Base):
    """Training subjects, i.e. discord users on a particular server who we will convert into models"""
    __tablename__ = 'subjects'
    id = Column(BigInteger, primary_key=True)
    discord_id = Column(BigInteger, unique=True)
    subject_name = Column(String(255))
    server_id = Column(BigInteger)
    server_name = Column(String(255))


class DataSet(Base):
    """Collected chat logs of our subjects"""
    __tablename__ = 'data_sets'
    id = Column(BigInteger, primary_key=True)
    subject_id = Column(BigInteger, ForeignKey('subjects.discord_id'))
    time_collected = Column(DateTime)
    data_uid = Column(String(32), unique=True)
    subject_foreign_key = relationship('Subject', foreign_keys=[subject_id])


class TextFilter(Base):
    """Text filters we apply to our data sets"""
    __tablename__ = 'filters'
    id = Column(BigInteger, primary_key=True)
    subject_id = Column(BigInteger, ForeignKey('subjects.id'))
    word = Column(String(255))
    subject_foreign_key = relationship('Subject', foreign_keys=[subject_id])


class MarkovModel(Base):
    """Markov chain models generated from our subject's chat history"""
    __tablename__ = 'markov_models'
    id = Column(BigInteger, primary_key=True)
    data_set_id = Column(BigInteger, ForeignKey('data_sets.id'))
    state_size = Column(Integer)
    newline = Column(Boolean)
    data_set_foreign_key = relationship('DataSet', foreign_keys=[data_set_id])


class Deployment(Base):
    """An encrypted markov chain model"""
    __tablename__ = 'deployments'
    id = Column(BigInteger, primary_key=True)
    secret_key = Column(String(255))
    markov_id = Column(BigInteger, ForeignKey('markov_models.id'))
    trainer_id = Column(BigInteger, ForeignKey('trainers.id'))
    markov_foreign_key = relationship('MarkovModel', foreign_keys=[markov_id])
    trainer_foreign_key = relationship('Trainer', foreign_keys=[trainer_id])
