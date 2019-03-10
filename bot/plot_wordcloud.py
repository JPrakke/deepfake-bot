import matplotlib.pyplot as plt
import s3fs
import gzip
from wordcloud import WordCloud, STOPWORDS
import multidict as multidict
import common.config


def get_frequency_dict(sentence):
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
    if filters == ['']:
        return ' '.join(content)

    filtered_content = ''
    counter = 0
    for mssg in content:
        include = True
        for filter_words in filters:
            if filter_words in mssg:
                include = False
                break
        if include:
            filtered_content += ' ' + mssg
            counter += 0

    return filtered_content, 0


def generate(data_id, filters, naughty=False):
    s3 = s3fs.S3FileSystem(key=common.config.aws_access_key_id,
                           secret=common.config.aws_secret_access_key)
    with s3.open(f'{common.config.aws_s3_bucket_prefix}/{data_id}-text.dsv.gz', mode='rb') as f:
        g = gzip.GzipFile(fileobj=f)
        content = g.read().decode().split(common.config.unique_delimiter)


    swear_path = './bot/resources/swearWords.txt'
    with open(swear_path, 'r') as f:
        swear_words = [i.strip() for i in f]

    if naughty:
        bad_language = ''
        for s in swear_words:
            bad_language = bad_language + (s + ' ') * content.lower().count(' ' + s + ' ')
        selected_text = bad_language
        if bad_language == '':
            return False, ''
    else:
        selected_text = apply_filters(content, filters)

    wc = WordCloud(background_color="black",
                   stopwords=STOPWORDS,
                   colormap='BrBG',
                   width=640,
                   height=480)

    wc.generate_from_frequencies(get_frequency_dict(selected_text))
    fig = plt.figure(frameon=False)
    ax = plt.Axes(fig, [0., 0., 1., 1.])
    ax.set_axis_off()
    fig.add_axes(ax)
    ax.imshow(wc, interpolation='bilinear')

    if naughty:
        file_name = f'./tmp/{data_id}-dirty-word-cloud.png'
    else:
        file_name = f'./tmp/{data_id}-word-cloud.png'

    fig.savefig(file_name)
    return True, file_name
