import pandas as pd
import matplotlib.pyplot as plt
import datetime as dt
import numpy as np
import boto3
import matplotlib.dates as mdates
from pandas.plotting import register_matplotlib_converters
from matplotlib import cm

register_matplotlib_converters()


def lambda_handler(event, context):

    # Read in arguments / event data
    data_uid = event['data_uid']
    user_name = event['user_name']

    # Download the data set from S3
    data_file_name = f'{data_uid}-channels.csv.gz'
    aws_s3_bucket_prefix = 'deepfake-discord-bot'
    s3 = boto3.resource('s3')
    s3.Bucket(aws_s3_bucket_prefix) \
        .download_file(data_file_name, '/tmp/' + data_file_name)

    # Make the plots
    activity_file = time_series_chart(data_uid, user_name)
    channels_file = channels_chart(data_uid, user_name)

    # Upload to S3
    s3.Object(aws_s3_bucket_prefix, activity_file).upload_file(f'/tmp/{activity_file}')
    s3.Object(aws_s3_bucket_prefix, channels_file).upload_file(f'/tmp/{channels_file}')

    return {
        'statusCode': 200,
        'image_file_names': [activity_file, channels_file]
    }


def day_filler(dates, counts):
    """Returns completed lists of dates and message counts with 0's added to every day with no messages"""
    def date_range(start_date, end_date):
        for n in range(int((end_date - start_date).days)):
            yield start_date + dt.timedelta(n)

    filled_dates = []
    filled_counts = []
    for single_date in date_range(dates.min(), dates.max()):
        filled_dates.append(single_date)
        if single_date in dates:
            i = np.where(dates == single_date)
            filled_counts.append(counts[i])
        else:
            filled_counts.append(0)

    return filled_dates, filled_counts


def auto_time_scale(td):
    """Used to format the x-axis based on the length of time to be plotted"""
    if td.days > 365:
        date_format = mdates.DateFormatter('%Y')
        major_tick = mdates.YearLocator()
    elif td.days > 30:
        date_format = mdates.DateFormatter('%b-%Y')
        major_tick = mdates.MonthLocator()
    elif td.days > 7:
        date_format = mdates.DateFormatter('%d %b-%Y')
        major_tick = mdates.DayLocator(interval=7)
    elif td.days > 1:
        date_format = mdates.DateFormatter('%d %b-%Y')
        major_tick = mdates.DayLocator()
    else:
        date_format = mdates.DateFormatter('%H:%M:%S')
        major_tick = mdates.HourLocator()

    return date_format, major_tick


def time_series_chart(data_id, user_name):
    """Plots a user's activity over time. I.e. number of messages vs. date"""

    # Open our file from S3 and read in the
    data_file_name = f'/tmp/{data_id}-channels.csv.gz'
    df = pd.read_csv(data_file_name, compression='gzip', encoding='utf-8')

    # Some data transformations
    df['datetime'] = df['timestamp'].apply(lambda t: dt.datetime.fromtimestamp(t))
    df['date'] = df['datetime'].apply(lambda t: t.date())

    ch_gb = df.groupby('date')
    message_dates = ch_gb['date'].count().index.values
    message_counts = ch_gb['timestamp'].count().values

    filled_dates, filled_counts = day_filler(message_dates, message_counts)

    # Make the time series plots
    fig, ax = plt.subplots()
    fig.set_figheight(7)
    fig.set_figwidth(10)

    ax.plot(filled_dates, filled_counts)
    ax.set_title(f'{user_name}\'s Activity')
    ax.set_ylabel('# messages')

    message_date_range = df['datetime'].max() - df['datetime'].min()
    auto_format, auto_tick = auto_time_scale(message_date_range)

    ax.xaxis.set_major_formatter(auto_format)
    ax.xaxis.set_major_locator(auto_tick)
    ax.grid()

    for tick in ax.get_xticklabels():
        tick.set_rotation(45)

    file_name = f'{data_id}-activity.png'
    fig.savefig(f'/tmp/{file_name}')
    return file_name


def channels_chart(data_id, user_name):
    """Plots a user's most active channels"""

    # Open our file from S3 and read in the
    data_file_name = f'/tmp/{data_id}-channels.csv.gz'
    df = pd.read_csv(data_file_name, compression='gzip', encoding='utf-8')

    # Some data transformations
    df['datetime'] = df['timestamp'].apply(lambda t: dt.datetime.fromtimestamp(t))
    df['day'] = df['datetime'].apply(lambda t: t.strftime("%A"))
    df['date'] = df['datetime'].apply(lambda t: t.date())

    ch_gb = df.groupby('channel')

    pie_labels = ch_gb['timestamp'].count().index.values
    pie_values = ch_gb['timestamp'].count().values

    # Make the channels pie chart
    fig, ax = plt.subplots()
    color_scale = cm.Blues(np.flip(np.arange(pie_labels.size)) / pie_labels.size)
    ax.pie(pie_values, labels=pie_labels, autopct='%1.1f%%', explode=[0.05]*pie_labels.size, colors=color_scale)
    ax.set_title(f'{user_name}\'s Favorite Channels')

    file_name_channels = f'{data_id}-pie-chart-channels.png'
    fig.savefig(f'/tmp/{file_name_channels}')

    return file_name_channels
