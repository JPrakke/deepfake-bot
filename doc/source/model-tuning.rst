Model Tuning
============

It might be that your model works perfectly on the first attempt. If not, there are a couple strategies to try. The best thing you can do is 
ensure that there is enough data, i.e. you have at least a few hundred quality messages of your subject on your server. Also, make sure 
DeepfakeBot can read all of the relevant channels.

Filtering
---------
To apply a filter use:

``df!filter add <@user> <word>``

Any messages containing your filter word will be ignored when generating another model. A common filter might be a bot command or prefix. Refer 
to the wordcloud image for other problematic words to filter.

.. tip:: Add ``@UNKOWN_USER`` as a filter.

Markovify Settings
------------------
You can also try reducing the Markov chain state size with:

``df!markovify state_size <@user> <new value>``

Or changing how it treats sentence endings with:

``df!markovify newline on <@user>``

Both of these options will tend to generate more chaotic, lower quality, sentences. Then again, it might be that your subject doesn't use 
complete sentences ``¯\_(ツ)_/¯``

To make a new model, you don't need to run the whole ``df!generate`` process again. Just use:

``df!markovify generate <@user>``

.. image:: https://deepfake-discord-bot-permanent.s3.us-east-1.amazonaws.com/markovify_generate.PNG
