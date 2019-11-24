Data Retention
==============

.. image:: https://deepfake-discord-bot-permanent.s3.amazonaws.com/Zuck.PNG

FAQ
---

What exactly are you doing with my data?
````````````````````````````````````````
As little as possible. I don't really want your data. I have no intention of selling any information or monetizing this beyond Patreon 
contributions. For the bot to function, however, it needs to read your servers' chat histories. And I do store some of these temporarily.

What sort of information do you store?
``````````````````````````````````````
Messages authored by your model subjects are uploaded as flat text files into an S3 bucket with a policy where objects expire every 24 hours. 
I also permanently store some information in a SQL database. For instance: your discord id and user name, your discord server id, any text 
filters you have applied. You can view the database schema `here <https://github.com/rustygentile/deepfake-bot/blob/master/cogs/db_schema.py>`_.

In the future, if I ever start offering to host your bot for you, I'll also need to store your encrypted model files. And these might contain 
sensitive information. Your model subject may have said things you're not aware of. Also, if I do decide to implement this feature, hosted bots 
won't be allowed to reply outside of the server on which they're trained.

Can I still use this without sharing anything?
``````````````````````````````````````````````
Absolutely! If this still makes you uncomfortable, you're also free to `fork <https://github.com/rustygentile/deepfake-bot>`_ the project and 
setup your own resources to run it. Contributions are welcome and encouraged. Keep in mind, though, that the code base is licensed with a GPL. 
So your fork will need to be open-source.
