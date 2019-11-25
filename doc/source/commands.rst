Command List
============

Common Commands
---------------

generate
````````

.. topic:: ``df!generate <@user>``

    Runs all of the process steps to create a model.

extract
```````

.. topic:: ``df!extract <@user>``

    Process step 1 of 4 from executing ``df!generate``. Extracts the chat history of a model subject. The bot will also provide the resulting files in case you want to try training a model on your own.

stats
`````

.. topic:: ``df!stats``

    Displays some stats about the bot.

Deploy Commands
---------------

deploy self
```````````

.. topic:: ``df!deploy self <@user>``

    Provides the model artifacts, secret key, and avatar URL for deploying your creation.

deploy hosted
`````````````

.. topic:: ``df!deploy hosted <@user> <token>``

    Not yet implemented.
 
Plot Commands
-------------

activity
````````

.. topic:: ``df!activity <@user>``

    Process step 2 of 4 from executing ``df!generate``. Plots a user activity and channels chart. 

wordcloud
`````````

.. topic:: ``df!wordcloud <@user>``

    Process step 3 of 4 from executing ``df!generate``. Generates a wordcloud image using your subject's chat history. Useful for adding filters.

dirtywordcloud
``````````````

.. topic:: ``df!dirtywordcloud <@user>``

    Generates a wordcloud image of swear words using your subject's chat history.

Filter Commands
---------------

filter add
``````````

.. topic:: ``df!filter add <@user> <word>``

    Adds a text filter for your model subject on the current server. Any messages containing this filter will be ignored.

filter remove
`````````````

.. topic:: ``df!filter remove <@user> <word>``

    Removes a text filter for your model subject on the current server.

filter show
```````````

.. topic:: ``df!filter show <@user>``

    Shows all active filters for your model subject on the current server.

filter clear_all
````````````````

.. topic:: ``df!filter clear_all <@user>``

    Removes all active filters for your model subject on the current server.

Model Commands
--------------

markovify generate
``````````````````

.. topic:: ``df!markovify generate <@user>``

    Process step 4 of 4 from executing ``df!generate``. Creates a Markov chain model using your subject's chat history and replies with sample responses.

markovify settings
``````````````````

.. topic:: ``df!markovify settings <@user>``

    Displays the current markovify settings for your subject on the current server. 

markovify state_size
````````````````````

.. topic:: ``df!markovify state_size <@user> <integer_value>``

    Changes the model state size for your subject on the current server. (Default value is 3). Reducing this tends to generate lower quality sentences.

markovify newline on
````````````````````

.. topic:: ``df!markovify newline on <@user>``

    Changes the sentence endings are treated for your subject on the current server. (Default value is off). Adding this tends to generate lower quality sentences.

markovify newline off
`````````````````````

.. topic:: ``df!markovify newline off <@user>``

    Disables the newline setting for your subject on the current server.
