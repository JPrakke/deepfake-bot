Model Tuning
============

`"The bot failed to generate a model for me. Now what?"`

If this happens, the first question you ask should be "is the bot seeing enough data?" You will likely need at least a
few hundred quality messages of your subject on your server for this to work. If however, you know there's enough good
data on your server and you find it isn't working, there are still a couple strategies to try.

Filtering
---------
To apply a filter use:

``df!filter add <@user> <word>``

Any messages containing your filter word will be ignored when generating another model. A common filter might be a bot command or prefix. Refer 
to the wordcloud image for other problematic words to filter. You might also want to try removing filters. When you
extract a data set, the bot will try to guess some filters to use. You can remove these with ``df!filter remove`` or
``df!filter clear_all``.

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
