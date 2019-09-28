import datetime as dt
import discord
from robot.schema import *
from robot.config import *
from sqlalchemy import create_engine
from sqlalchemy.orm import Session


def check_connection(session):
    result = session.query(Trainer).all()
    print(f'Connected... # of registered users: {len(result)}')


def ping_connection(session):
    session.query(Trainer).first()


def register_trainer(session, ctx):
    """Registers bot users"""
    id_to_check = int(ctx.message.author.id)
    result = session.query(Trainer) \
                    .filter(Trainer.discord_id == id_to_check) \
                    .all()

    # If no record exists, add one.
    if len(result) == 0:
        new_user = Trainer(
            discord_id=int(ctx.message.author.id),
            user_name=f'{ctx.message.author.name}#{ctx.message.author.discriminator}',
            time_registered=dt.datetime.utcnow()
        )
        session.add(new_user)
        session.commit()


def register_subject(session, ctx, subject: discord.member):
    """Registers training subjects"""
    user_id_to_check = int(subject.id)
    server_id_to_check = int(ctx.message.guild.id)

    result = session.query(Subject) \
                    .filter(Subject.discord_id == user_id_to_check,
                            Subject.server_id == server_id_to_check) \
                    .all()

    # If no record exists, add one.
    if len(result) == 0:
        new_user = Subject(
            discord_id=int(subject.id),
            subject_name=f'{subject.name}#{subject.discriminator}',
            server_id=int(ctx.message.guild.id),
            server_name=ctx.message.guild.name
        )
        session.add(new_user)
        session.commit()


def create_data_set(session, ctx, user_mention, uid):
    """Adds a record for when a data set is created"""

    subject_id = session.query(Subject) \
                        .filter(Subject.discord_id == int(user_mention.id),
                                Subject.server_id == int(ctx.message.guild.id))\
                        .first().id

    new_data_set = DataSet(
        subject_id=subject_id,
        time_collected=dt.datetime.utcnow(),
        data_uid=uid
    )
    session.add(new_data_set)
    session.commit()


async def get_latest_dataset(session, ctx, user_mention):
    """Finds the most recent data set for a particular subject on a particular server. Returns False if no data found"""
    result = session.query(DataSet) \
                    .join(Subject) \
                    .filter(Subject.discord_id == int(user_mention.id),
                            Subject.server_id == int(ctx.message.guild.id))\
                    .order_by(DataSet.id.desc()).first()

    try:
        data_set = result
        if (dt.datetime.utcnow() - data_set.time_collected).days < 1:
            return data_set.data_uid
        else:
            await ctx.message.channel.send(
                  f'The only data set I found on this server for {user_mention.name} is expired.')
            await ctx.message.channel.send(f'Try running `df!extract` again.')
            # TODO: Add a link to data retention policy once it's done
            return False
    except (TypeError, AttributeError):
        await ctx.message.channel.send(
              f'I couldn\'t find a data set for {user_mention.name}. Try running `df!extract` first.')
        return False


def add_a_filter(session, ctx, subject: discord.member, word_to_add):
    """Adds a text filter for a given subject"""
    register_subject(session, ctx, subject)

    if session.query(TextFilter) \
              .join(Subject) \
              .filter(TextFilter.word == word_to_add,
                      Subject.server_id == int(ctx.message.guild.id),
                      Subject.discord_id == int(subject.id)) \
              .count() == 0:
        filter_record = TextFilter(
            subject_id=session.query(Subject)
                              .filter(Subject.server_id == int(ctx.message.guild.id),
                                      Subject.discord_id == int(subject.id))
                              .first().id,
            word=word_to_add
        )
        session.add(filter_record)
        session.commit()


def remove_a_filter(session, ctx, subject: discord.member, word_to_remove):
    """Removes a text filter for a given subject. Returns False if no such filter is found."""
    register_subject(session, ctx, subject)
    filter_records = session.query(TextFilter) \
                            .join(Subject) \
                            .filter(TextFilter.word == word_to_remove,
                                    Subject.server_id == int(ctx.message.guild.id),
                                    Subject.discord_id == int(subject.id)) \
                            .all()

    if len(filter_records) > 0:
        [session.delete(r) for r in filter_records]
        session.commit()
        return True
    else:
        return False


def clear_filters(session, ctx, subject: discord.member):
    """Clears all text filters for a given subject."""
    register_subject(session, ctx, subject)
    filter_records = session.query(TextFilter) \
                            .join(Subject) \
                            .filter(Subject.server_id == int(ctx.message.guild.id),
                                    Subject.discord_id == int(subject.id)) \
                            .all()

    [session.delete(r) for r in filter_records]
    session.commit()


def find_filters(session, ctx, subject: discord.member):
    """Returns all the text filters for a given subject"""
    register_subject(session, ctx, subject)
    filter_records = session.query(TextFilter) \
                            .join(Subject) \
                            .filter(Subject.server_id == int(ctx.message.guild.id),
                                    Subject.discord_id == int(subject.id)) \
                            .all()

    return [res.word for res in filter_records]


def make_tables():
    engine = create_engine(database_url)
    conn = engine.connect()
    Base.metadata.create_all(conn, checkfirst=False)
    session = Session(engine)
    check_connection(session)


if __name__ == '__main__':
    print(database_url)
    make_tables()
