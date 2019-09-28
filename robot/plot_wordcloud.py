import matplotlib.pyplot as plt
import s3fs
import gzip
from wordcloud import WordCloud, STOPWORDS
import multidict as multidict
import robot.config


def get_frequency_dict(sentence):
    """Converts raw text into a multidict for wordcloud usage"""
    full_terms_dict = multidict.MultiDict()
    tmp_dict = {}

    # making dict for counting frequencies
    for text in sentence.split(" "):
        if text.lower().strip() in STOPWORDS:
            continue
        val = tmp_dict.get(text, 0)
        tmp_dict[text.strip()] = val + 1
    for key in tmp_dict:
        full_terms_dict.add(key, tmp_dict[key])
    return full_terms_dict


def apply_filters(content, filters):
    """Filters messages based on a list of words. If a filter word is present in a message, that message is removed."""
    if filters == ['']:
        return content

    filtered_content = []
    for mssg in content:
        include = True
        for filter_words in filters:
            if filter_words in mssg:
                include = False
                break
        if include:
            filtered_content.append(mssg)

    return filtered_content


def get_s3_content(data_id):
    """Reads in data from S3 file"""
    s3 = s3fs.S3FileSystem(key=robot.config.aws_access_key_id,
                           secret=robot.config.aws_secret_access_key)
    with s3.open(f'{robot.config.aws_s3_bucket_prefix}/{data_id}-text.dsv.gz', mode='rb') as f:
        g = gzip.GzipFile(fileobj=f)
        content = g.read().decode().split(robot.config.unique_delimiter)

    return content


def generate_dirty(data_id):
    """Makes a word cloud of swear words for a subject. No filters applied."""
    content = ' '.join(get_s3_content(data_id))

    swear_path = './robot/resources/swearWords.txt'
    with open(swear_path, 'r') as f:
        swear_words = [i.strip() for i in f]

        bad_language = ''
        for s in swear_words:
            bad_language = bad_language + (s + ' ') * content.lower().count(' ' + s + ' ')
        if bad_language == '':
            return False

    wc = WordCloud(background_color="black",
                   stopwords=STOPWORDS,
                   colormap='BrBG',
                   width=640,
                   height=480)

    wc.generate_from_frequencies(get_frequency_dict(bad_language))
    fig = plt.figure(frameon=False)
    ax = plt.Axes(fig, [0., 0., 1., 1.])
    ax.set_axis_off()
    fig.add_axes(ax)
    ax.imshow(wc, interpolation='bilinear')

    file_name = f'./tmp/{data_id}-dirty-word-cloud.png'
    fig.savefig(file_name)
    return file_name


def generate(data_id, filters):
    """Makes a wordcloud of a user's messages with filters applied"""
    content = get_s3_content(data_id)
    selected_content = apply_filters(content, filters)

    wc = WordCloud(background_color="black",
                   stopwords=STOPWORDS,
                   colormap='BrBG',
                   width=640,
                   height=480)

    wc.generate_from_frequencies(get_frequency_dict(' '.join(selected_content)))
    fig = plt.figure(frameon=False)
    ax = plt.Axes(fig, [0., 0., 1., 1.])
    ax.set_axis_off()
    fig.add_axes(ax)
    ax.imshow(wc, interpolation='bilinear')

    file_name = f'./tmp/{data_id}-word-cloud.png'

    fig.savefig(file_name)
    return file_name, len(content), len(selected_content)
