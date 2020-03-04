Interacting With Your Bot
=========================

Bot Bevahior
------------
By default, your bot will randomly reply to messages in the channels for which it has permission to do so. The bot will select one of 1000 randomly generated Markov chains based the message to which it replies. It will also occasionally try to strike up a conversation on its own. You can tweak this behavior by adjusting the parameters below.

Configuring
-----------
To configure your bot, you may edit the parameters in ``<model-uid>-config.json`` before uploading it to Cloudcube. You can also reconfigure your bot using:

``<prefix>config set <parameter name> <new parameter value>``

Only the bot owner will have permission to use this command. When this command is used, the file in Cloudcube will automatically be updated.

Parameters
``````````
* ``reply_probability`` - Increase this to make your bot more likely to reply at random. 
* ``new_conversation_min_wait`` - Minimum time before your bot starts a new conversation. If ``reply_probability`` is 0, no new conversations will be started.
* ``new_conversation_max_wait`` - Minimum time before your bot starts a new conversation. If ``reply_probability`` is 0, no new conversations will be started.
* ``max_sentence_length`` - Maximum number of characters in your bot's replies.
* ``max_markov_chains`` - Maximum number of Markov chains to attempt to generate per candiate reply. 
* ``selection_algorithm`` - Can be 'cosine_similarity' or 'match_words'. When replying, this is how your bot will select the best response from its Markov chain candiates.
* ``quiet_mode`` - Removes ``@`` s from replies.
* ``avg_delay`` - Average time before starting to type a response.
* ``std_dev_delay`` - Variance in time before starting to type a response.
* ``min_delay`` - Minimum time before starting to type a response.
* ``avg_typing_speed`` - Average typing speed in WPM.
* ``std_dev_typing_speed`` - Variance in typing speed in WPM.
* ``min_typing_speed`` - Minimum typing speed in WPM.
* ``white_list_server_ids`` - A list of servers where your bot can reply. By default, this is only the server on which it was trained.
* ``owner_id`` - Your discord id.
* ``bot_prefix`` - Command prefix for your bot. Make sure it is unique for the server(s) on which it runs.
* ``version`` - Bot version used to generate your model artifacts.

Commands
--------
impersonate
```````````
.. topic:: ``<prefix>impersonate``

    Bot will reply in a style similar to its training subject.

config set
``````````
.. topic:: ``<prefix>config set <parameter name> <new parameter value>``

    Changes a configuration parameter. Only the bot owner will have permission to do this.

config show
```````````
.. topic:: ``<prefix>config show``

    Displays the current configuration.

catfact 
```````
.. topic:: ``<prefix>catfact``

    Replies with a random cat fact.

catpic 
``````
.. topic:: ``<prefix>catpic``

    Replies with a random cat pic.

asciify 
```````
.. topic:: ``<prefix>asciify <your message>``

    Converts your message into ascii art.