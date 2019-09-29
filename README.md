# DeepfakeBot

(work in progress...)

### *"That's kinda creepy"* 

Make copies of your friends! Using the magic of cloud computing, [markov](https://github.com/jsvine/markovify) chains and a little data analytics, you can create a bot that sounds like another discord user.

## Proccess
* [Add](https://discordapp.com/oauth2/authorize?client_id=551871268090019945&scope=bot&permissions=117760) DeepfakeBot to your server.
* Extract your subject's chat history with `df!extract <@user#0000>`.
* Explore the dataset with `df!wordcloud` and `df!activity`. Use this to determine how to filter messages from your model.
* Clean your data with `df!filter`. Remove messages that don't contain real sentences.
* Create a Markov chain generator with `df!markovify`. This will generate random sentences which sound similar to your subject.

Once you're happy with the results, the bot will message your model artifacts to you and you'll be ready to deploy!

## Deployment
### *"why do i sound like i have a speech peppermint?"*

Before you get started, you will need:
* A Github account (to fork this project) 
* A Heroku account (to host your bot)
* A Discord developer account to create your bot's account

A basic knowledge of python is helpful too. But don't worry, you won't need to do any actual coding.

To be continued...
