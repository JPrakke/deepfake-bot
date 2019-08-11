import pandas as pd
import matplotlib.pyplot as plt
import s3fs
import datetime as dt
import numpy as np
import matplotlib.dates as mdates
import robot.config
from pandas.plotting import register_matplotlib_converters

register_matplotlib_converters()


def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days)):
        yield start_date + dt.timedelta(n)


def day_filler(dates, counts):
    filled_dates = []
    filled_counts = []
    for single_date in daterange(dates.min(), dates.max()):
        filled_dates.append(single_date)
        if single_date in dates:
            i = np.where(dates == single_date)
            filled_counts.append(counts[i])
        else:
            filled_counts.append(0)

    return filled_dates, filled_counts


def auto_time_scale(td):

    if td.days < 1:
        date_format = mdates.DateFormatter('%H:%M:%S')
        major_tick = mdates.HourLocator()
    elif td.days < 7:
        date_format = mdates.DateFormatter('%d %b-%Y')
        major_tick = mdates.DayLocator()
    elif td.days < 30:
        date_format = mdates.DateFormatter('%d %b-%Y')
        major_tick = mdates.DayLocator(interval=7)
    elif td.days < 365:
        date_format = mdates.DateFormatter('%b-%Y')
        major_tick = mdates.MonthLocator()
    else:
        date_format = mdates.DateFormatter('%Y')
        major_tick = mdates.YearLocator()

    return date_format, major_tick


def generate(data_id, user_name):
    s3 = s3fs.S3FileSystem(key=robot.config.aws_access_key_id,
                           secret=robot.config.aws_secret_access_key)
    with s3.open(f'{robot.config.aws_s3_bucket_prefix}/{data_id}-channels.tsv.gz', mode='rb') as f:
        df = pd.read_csv(f, compression='gzip', encoding='utf-8')

    df['datetime'] = df['timestamp'].apply(lambda t: dt.datetime.fromtimestamp(t))
    df['day'] = df['datetime'].apply(lambda t: t.weekday())
    df['date'] = df['datetime'].apply(lambda t: t.date())

    ch_gb = df.groupby('date')
    message_dates = ch_gb['date'].count().index.values
    message_counts = ch_gb['timestamp'].count().values

    filled_dates, filled_counts = day_filler(message_dates, message_counts)

    fig, ax = plt.subplots()
    fig.set_figheight(7)
    fig.set_figwidth(10)

    ax.plot(filled_dates, filled_counts)
    ax.set_title(f'{user_name}\'s Activity')
    ax.set_ylabel('# messages')

    date_range = df['datetime'].iloc[0] - df['datetime'].iloc[len(df)-1]
    auto_format, auto_tick = auto_time_scale(date_range)

    ax.xaxis.set_major_formatter(auto_format)
    ax.xaxis.set_major_locator(auto_tick)
    ax.grid()

    for tick in ax.get_xticklabels():
        tick.set_rotation(45)

    file_name = f'./tmp/{data_id}-activity.png'
    fig.savefig(file_name)
    return file_name


def bar_charts(data_id, user_name):
    s3 = s3fs.S3FileSystem(key=robot.config.aws_access_key_id,
                           secret=robot.config.aws_secret_access_key)
    with s3.open(f'{robot.config.aws_s3_bucket_prefix}/{data_id}-channels.tsv.gz', mode='rb') as f:
        df = pd.read_csv(f, compression='gzip', encoding='utf-8')

    df['datetime'] = df['timestamp'].apply(lambda t: dt.datetime.fromtimestamp(t))
    df['day'] = df['datetime'].apply(lambda t: t.weekday())
    df['date'] = df['datetime'].apply(lambda t: t.date())

    # Don't make bar charts if only one channel
    if len(df['channel'].unique()) < 2:
        return False, False

    ch_gb = df.groupby('channel')

    bar_labels = ch_gb['timestamp'].count().index.values
    bar_values = ch_gb['timestamp'].count().values

    bar_values, bar_labels = (list(t) for t in zip(*sorted(zip(bar_values, bar_labels),
                                                           reverse=True)))

    fig, ax = plt.subplots()
    fig.set_figheight(7)
    fig.set_figwidth(10)
    plt.subplots_adjust(bottom=0.2)

    ax.bar(bar_labels, bar_values)
    ax.set_title(f'{user_name}\'s Favorite Channels')
    ax.set_ylabel('# messages')
    ax.grid()

    for tick in ax.get_xticklabels():
        tick.set_rotation(45)

    file_name = f'./tmp/{data_id}-bar-chart.png'
    fig.savefig(file_name)

    # Log scale plot to show all the channels clearer
    fig, ax = plt.subplots()
    fig.set_figheight(7)
    fig.set_figwidth(10)
    plt.subplots_adjust(bottom=0.2)

    ax.bar(bar_labels, bar_values)
    ax.set_title(f'{user_name}\'s Favorite Channels\n (log scale)')
    ax.set_ylabel('# messages')
    ax.set_yscale('log')
    ax.grid()

    for tick in ax.get_xticklabels():
        tick.set_rotation(45)

    file_name_log = f'./tmp/{data_id}-bar-chart-log.png'
    fig.savefig(file_name_log)

    return file_name, file_name_log
