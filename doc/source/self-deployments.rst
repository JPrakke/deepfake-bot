Self Deployments
================
"I ran all of the bot commands you told me to and it gave me some files. Now what?"

Prerequisites
-------------
To host your bot you will need:

1. A `Discord <https://discordapp.com/developers/>`_ developer account.
2. A `Github <https://github.com>`_ account. You won't need to do any actual coding for this.
3. A `Heroku <https://heroku.com/>`_ account. You can do this using only free resources but you should verify your account.

Deployment Steps
----------------
Discord
```````
1. Create a new `application <https://discordapp.com/developers/applications/>`_ and add a bot to it.
2. Change its icon to the avatar you received in a private message from running ``df!deploy self``.
3. Copy the bot's token (not the application's client secret) and keep it somewhere safe.

Also, make sure you download the files from Discord. You can edit the parameters in `*-config.json` but do not rename either file.

.. image:: https://deepfake-discord-bot-permanent.s3.us-east-1.amazonaws.com/model_artifacts.PNG

Github
``````
Head over `here <https://github.com/rustygentile/deepfake-bot>`_ and create a fork. Don't write any new code or push any changes unless you 
feel like doing so.

Heroku
``````
Create a new app in `Heroku <https://dashboard.heroku.com/apps>`_ . You can host several bots in a single app. With free resources I was able to 
run three of them. And if you want more bots you always can create more apps.

.. image:: https://deepfake-discord-bot-permanent.s3.amazonaws.com/new_heroku_app.PNG

Under the **Deploy** tab link the app to your Github repository.

.. image:: https://deepfake-discord-bot-permanent.s3.amazonaws.com/link_to_github.PNG

Under **Automatic Deploys** select the ``self-deployment`` branch and enable automatic deploys.

.. image:: https://deepfake-discord-bot-permanent.s3.amazonaws.com/select_branch.PNG

Run a manual deploy while you're here.

.. image:: https://deepfake-discord-bot-permanent.s3.amazonaws.com/manual_deploy.PNG

Under the **Resources** tab search for "Cloudcube" in **Add-ons**. Provision a free plan. Then open the link in a new tab.

.. image:: https://deepfake-discord-bot-permanent.s3.amazonaws.com/add_cloudcube.PNG

Click **Upload Files** in the upper right hand corner of your Cloudcube page. You should upload both the ``*-config.json`` and 
``*-markov-model-encrypted.json.gz`` files and keep them private.

.. image:: https://deepfake-discord-bot-permanent.s3.amazonaws.com/upload_cloudcube_files.PNG

Go back to your Heroku app under the **Resources** tab and click **Reveal Config Vars**. You should see some variables from Cloudcube. Don't 
touch these.

.. image:: https://deepfake-discord-bot-permanent.s3.amazonaws.com/reveal_config_vars.PNG

But do add the following environment variables:

* ``DEEPFAKE_MODEL_UID_1`` - this will be the file prefix for your model artifacts
* ``DEEPFAKE_SECRET_KEY_1`` - this will be the secret key that you should have received in a private message from DeepfakeBot
* ``DEEPFAKE_BOT_TOKEN_1`` - this will be the bot token you copied earlier

To run multiple bots, add more model artifacts to your Cloudcube folder and create ``DEEPFAKE_MODEL_UID_2``, ``DEEPFAKE_SECRET_KEY_2``,  
``DEEPFAKE_BOT_TOKEN_2`` and so forth.

You can add up to 10 such environment variable trios by default. You'll quickly run out of Cloudcube space and dyno memory on a free plan 
however.

Proceed to the **Resources** tab and enable a free worker dyno. Your bot should start running now.

.. image:: https://deepfake-discord-bot-permanent.s3.amazonaws.com/enable_dyno.PNG

To verify everything is working, go to the upper right corner and click **More** --> **View logs**.

.. image:: https://deepfake-discord-bot-permanent.s3.amazonaws.com/view_logs.PNG

You should see something like this eventually:

.. code-block:: text

    2019-11-24T21:24:19.779681+00:00 app[worker.1]: INFO:cogs.config_cog:Logged in as
    2019-11-24T21:24:19.779766+00:00 app[worker.1]: INFO:cogs.config_cog:<name>
    2019-11-24T21:24:19.779863+00:00 app[worker.1]: INFO:cogs.config_cog:<id>

That's it! Your bot is up and running. Now go add it to your Discord server.