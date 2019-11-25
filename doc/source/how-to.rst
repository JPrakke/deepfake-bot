Quick Start / How-to
====================

Add the bot
-----------
Use `this <https://discordapp.com/oauth2/authorize?client_id=551871268090019945&scope=bot&permissions=117760>`_ link to add the bot to 
your server. Make sure it has permission to view the text channels it needs. Of course, you might also want to restrict its access to 
certain channels.

Generate
--------
.. tip:: Use a private channel so that your subject won't see what you're doing

To generate a model of your target user, execute:

``df!generate <@user>``

.. image:: https://deepfake-discord-bot-permanent.s3.amazonaws.com/generate_start.PNG

This will likely take a few minutes. The bot will read your server's chat history, give you some stats on your subject's messages, and 
generate a Markov chain model that mimics them. If, at the end of the process you get something that sounds like your subject you can 
proceed. Note the ``model_uid`` that gets generated:

.. image:: https://deepfake-discord-bot-permanent.s3.us-east-1.amazonaws.com/good_markov.PNG

If, on the other hand, you get something like this see `here <./model-tuning.html>`_:

.. image:: https://deepfake-discord-bot-permanent.s3.us-east-1.amazonaws.com/bad_markov.PNG

Deploy
------
Once you're happy with the model you've created use:

``df!deploy self <@user>``

The bot then will provide the files you need and a secret key for decrypting them. See `here <./self-deployments.html>`_ for 
what to do with your model artifacts.

.. image:: https://deepfake-discord-bot-permanent.s3.us-east-1.amazonaws.com/model_artifacts.PNG
