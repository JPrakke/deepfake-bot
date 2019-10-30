import datetime as dt
import discord
from cogs.db_schema import *
from cogs.config import *
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
import logging

logger = logging.getLogger(__name__)


def check_connection(session):
    """Should show a healthy connection when the bot starts"""
    result = session.query(Trainer).all()
    logger.info(f'Connected... # of registered users: {len(result)}')


def ping_connection(session):
    """Uses this to make sure the connection is kept open"""
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


def get_markov_settings(session, ctx, subject: discord.member):
    """Returns the current markov settings for a given subject (or defaults if no record exists)"""
    register_subject(session, ctx, subject)
    markov_records = session.query(MarkovSettings) \
                            .join(Subject) \
                            .filter(Subject.server_id == int(ctx.message.guild.id),
                                    Subject.discord_id == int(subject.id)) \
                            .all()

    if len(markov_records) == 1:
        return markov_records[0].state_size, markov_records[0].newline
    else:
        return 3, False


def update_markov_settings(session, ctx, subject: discord.member, new_state_size, new_newline):
    """Updates the markov settings for a user or creates a new record if none exists"""
    register_subject(session, ctx, subject)
    markov_records = session.query(MarkovSettings) \
                            .join(Subject) \
                            .filter(Subject.server_id == int(ctx.message.guild.id),
                                    Subject.discord_id == int(subject.id)) \
                            .all()

    if len(markov_records) == 1:
        # If a record is found, just update it
        markov_records[0].state_size = new_state_size
        markov_records[0].newline = new_newline
        session.commit()
    else:
        # It's unlikely that there will be more than one record but still, let's make sure...
        for record in markov_records:
            session.delete(record)

        # Add the new settings
        new_record = MarkovSettings(
            subject_id=session.query(Subject)
                              .filter(Subject.server_id == int(ctx.message.guild.id),
                                      Subject.discord_id == int(subject.id))
                              .first().id,
            state_size=new_state_size,
            newline=new_newline
        )
        session.add(new_record)
        session.commit()


def create_markov_model(session, data_set_uid, model_uid):
    """Adds a record for when a Markov model is generated"""
    data_set_id = session.query(DataSet) \
                         .filter(DataSet.data_uid == data_set_uid)\
                         .first().id

    new_markov_model = MarkovModel(
        data_set_id=data_set_id,
        time_collected=dt.datetime.utcnow(),
        model_uid=model_uid
    )
    session.add(new_markov_model)
    session.commit()


async def get_latest_markov_model(session, ctx, user_mention):
    """Works similar to get_latest_dataset(). Returns False if no data found"""
    result = session.query(MarkovModel) \
                    .join(DataSet) \
                    .join(Subject) \
                    .filter(Subject.discord_id == int(user_mention.id),
                            Subject.server_id == int(ctx.message.guild.id))\
                    .order_by(MarkovModel.id.desc()).first()

    try:
        markov_model = result
        if (dt.datetime.utcnow() - markov_model.time_collected).days < 1:
            return markov_model.model_uid
        else:
            await ctx.message.channel.send(
                  f'The only model I found on this server for {user_mention.name} is expired.')
            await ctx.message.channel.send(f'Try running `df!markovify generate` again.')
            # TODO: Add a link to data retention policy once it's done
            return False
    except (TypeError, AttributeError):
        await ctx.message.channel.send(
              f'I couldn\'t find a model for {user_mention.name}. Try running `df!markovify generate` first.')
        return False


def create_deployment(session, ctx, model_uid, secret_key, bot_token=''):
    """Records a new deployment. If no bot token is provided, assume it's a self deployment."""
    markov_id = session.query(MarkovModel) \
        .filter(MarkovModel.model_uid == model_uid) \
        .first().id

    trainer_id = session.query(Trainer)\
                        .filter(Trainer.discord_id == ctx.message.author.id)\
                        .first().id

    new_deployment = Deployment(
        secret_key=secret_key,
        markov_id=markov_id,
        trainer_id=trainer_id,
        hosted=bot_token is not ''
    )
    session.add(new_deployment)
    session.flush()

    if bot_token:
        # Create a new record with default settings
        new_hosted_deployment = HostedDeployment(
            deployment_id=new_deployment.id,
            ip_address='0.0.0.0',
            active=True,
            reply_probability=0.3,
            new_conversation_min_wait=60,
            new_conversation_max_wait=3600,
            max_sentence_length=250,
            quiet_mode=False,
            bot_token=bot_token
        )
        session.add(new_hosted_deployment)

    session.commit()


def make_tables():
    """Creates the tables in our database schema"""
    engine = create_engine(database_url)
    conn = engine.connect()
    Base.metadata.create_all(conn, checkfirst=False)
    session = Session(engine)
    check_connection(session)


if __name__ == '__main__':
    """Only run this file if you want to create the schema"""
    logger.info(database_url)
    make_tables()
