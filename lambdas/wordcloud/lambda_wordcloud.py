import matplotlib.pyplot as plt
from wordcloud import WordCloud, STOPWORDS
import multidict as multidict
import boto3
import gzip
import json


def lambda_handler(event, context):
    # Read in arguments / event data
    data_uid = event['data_uid']
    filters = event['filters']
    wordcloud_file_name = event['wordcloud_file_name']
    dirty = event['dirty']

    # Download the data set from S3
    text_file_name = f'{data_uid}-text.dsv.gz'
    aws_s3_bucket_prefix = 'deepfake-discord-bot'
    s3 = boto3.resource('s3')
    s3.Bucket(aws_s3_bucket_prefix) \
        .download_file(text_file_name, '/tmp/' + text_file_name)

    # Decompress
    with open('/tmp/' + text_file_name, 'rb') as f:
        g = gzip.GzipFile(fileobj=f)
        content = g.read().decode(). \
            split('11a4b96a-ae8a-45f9-a4db-487cda63f5bd')

    # Apply filters
    if filters == ['']:
        filtered_content = content
    else:
        filtered_content = []
        for i in content:
            include = True
            for j in filters:
                if j in i:
                    include = False
                    break
            if include:
                filtered_content.append(i)

    if dirty:
        swears = generate_dirty(filtered_content, wordcloud_file_name)
        response = {
            'statusCode': 200,
            'swears': swears
        }

    else:
        generate(filtered_content, wordcloud_file_name)
        response = {
            'statusCode': 200,
            'total_messages': len(content),
            'filtered_messages': len(filtered_content)
        }

    # Upload to S3
    s3.Object(aws_s3_bucket_prefix, wordcloud_file_name) \
        .upload_file(f'/tmp/{wordcloud_file_name}')

    # Upload the response to S3 as a .json file
    response_file_name = wordcloud_file_name.replace('.png', '.json')
    with open(f'/tmp/{response_file_name}', 'w') as f:
        f.write(json.dumps(response))

    s3.Object(aws_s3_bucket_prefix, response_file_name) \
        .upload_file(f'/tmp/{response_file_name}')

    return response


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


def generate_dirty(content, file_name):
    """Makes a word cloud of swear words for a subject. No filters applied."""
    content = ' '.join(content)

    swear_path = './resources/swearWords.txt'
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

    fig.savefig(f'/tmp/{file_name}')
    return True


def generate(selected_content, file_name):
    """Makes a wordcloud of a user's messages with filters applied"""
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

    fig.savefig(f'/tmp/{file_name}')
