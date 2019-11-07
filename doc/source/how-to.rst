Quick Start / How-to
====================

Add the bot
-----------
Use `this <https://discordapp.com/oauth2/authorize?client_id=551871268090019945&scope=bot&permissions=117760>`_ link to add the bot to 
your server. Make sure it has permission to view the text channels it needs. Of course, you might also want to restrict its access to 
certain channels.

Generate
--------
To generate a model of your target user, execute:

``df!generate <@user>``

This will likely take a few minutes. The bot will read your server's chat history, give you some stats on your subject's messages, and 
generate a Markov chain model that mimics them.

Tune
----
It might be that your model works perfectly on the first attempt. If not, there are a couple strategies to try.

Filtering
`````````
To apply a filter use:

``df!filter add <@user> <word>``

Any messages containing your filter word will be ignored when generating another model. A common filter might be a bot command or prefix. 
You may also want to add ``@UNKOWN_USER`` as a filter. Refer to the wordcloud image for other ideas.

Markovify Settings
``````````````````
You can also try reducing the Markov chain state size with:

``df!markovify state_size <@user> <new value>``

Or changing how it treats sentence endings with:

``df!markovify newline on <@user>``

Both of these options will tend to generate more chaotic, lower quality, sentences. Then again, it might be that your subject doesn't use 
complete sentences. 

Deploy
------
Once you're happy with the model you've generated use:

``df!deploy self <@user>``

The bot then will provide the model artifacts you need and a secret key for decrypting them. See `here <./self-deployments.html>`_ for 
what to do with your model artifacts.
