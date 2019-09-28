import pandas as pd
import matplotlib.pyplot as plt
import s3fs
import datetime as dt
import numpy as np
import matplotlib.dates as mdates
import robot.config
from pandas.plotting import register_matplotlib_converters
from matplotlib import cm

register_matplotlib_converters()


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

    # Open our file from S3 and read in the data
    s3 = s3fs.S3FileSystem(key=robot.config.aws_access_key_id,
                           secret=robot.config.aws_secret_access_key)
    with s3.open(f'{robot.config.aws_s3_bucket_prefix}/{data_id}-channels.tsv.gz', mode='rb') as f:
        df = pd.read_csv(f, compression='gzip', encoding='utf-8')

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

    file_name = f'./tmp/{data_id}-activity.png'
    fig.savefig(file_name)
    return file_name


def pie_charts(data_id, user_name):
    """Plots a user's most active channels and days of the week"""

    # Open our file from S3 and read in the data
    s3 = s3fs.S3FileSystem(key=robot.config.aws_access_key_id,
                           secret=robot.config.aws_secret_access_key)
    with s3.open(f'{robot.config.aws_s3_bucket_prefix}/{data_id}-channels.tsv.gz', mode='rb') as f:
        df = pd.read_csv(f, compression='gzip', encoding='utf-8')

    # Some data transformations
    df['datetime'] = df['timestamp'].apply(lambda t: dt.datetime.fromtimestamp(t))
    df['day'] = df['datetime'].apply(lambda t: t.strftime("%A"))
    df['date'] = df['datetime'].apply(lambda t: t.date())

    ch_gb = df.groupby('channel')
    day_gb = df.groupby('day')

    pie_labels = ch_gb['timestamp'].count().index.values
    pie_values = ch_gb['timestamp'].count().values

    day_labels = day_gb['timestamp'].count().index.values
    day_values = day_gb['timestamp'].count().values

    # Make the channels pie chart
    fig, ax = plt.subplots()
    color_scale = cm.Blues(np.flip(np.arange(pie_labels.size)) / pie_labels.size)
    ax.pie(pie_values, labels=pie_labels, autopct='%1.1f%%', explode=[0.05]*pie_labels.size, colors=color_scale)
    ax.set_title(f'{user_name}\'s Favorite Channels')

    file_name_channels = f'./tmp/{data_id}-pie-chart-channels.png'
    fig.savefig(file_name_channels)

    # Make the days of the week pie chart
    fig, ax = plt.subplots()
    color_scale = cm.Blues(np.flip(np.arange(day_labels.size)) / day_labels.size)
    ax.pie(day_values, labels=day_labels, autopct='%1.1f%%', explode=[0.05]*day_labels.size, colors=color_scale)
    ax.set_title(f'{user_name}\'s Most Active Days')

    file_name_days = f'./tmp/{data_id}-pie-chart-days.png'
    fig.savefig(file_name_days)

    return file_name_channels, file_name_days
