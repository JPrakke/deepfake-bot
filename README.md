# DeepfakeBot

UPDATE (2021): This was a fun project but unfortunately there hasn't been enough interest in it to justify my AWS bill. So I've decided to take the bot down. Thank  you to everyone who used it. And thank you for all of the (mostly) positive feedback.

---
Make copies of your friends! Using the magic of cloud computing, [Markov](https://github.com/jsvine/markovify) chains and a little data analytics, you can create a bot that sounds like another discord user.

## Users

* [~~Add~~]() the bot to your Discord server.
* [Read](https://deepfake-bot.readthedocs.io/) about how to use it.
* Get [~~help~~]() with your bot if you get stuck. 
* [~~Donate~~]() to keep the bot up and running.

## Developers

This is meant to be a rough outline of the steps and AWS resources needed to get this project up and running. It is not a precise how-to as I'm probably forgetting one or more steps. If you're a normal user ready deploy your bot, skip this section and see [here](https://deepfake-bot.readthedocs.io/en/latest/self-deployments.html) instead.

### VPC

* Setup a VPC with public and private subnets.
* Setup a route table to allow traffic in the public subnets to an internet gateway.
* In the private subnet, allow only traffic to and from the public subnet.

### Database

* Provision a MySQL RDS instance in one of your private subnets. Create a master user and password.
* Provision an EC2 instance in one of your public subnets.
* Use an SSH tunnel to this to enable a database connection from a terminal on your development machine: ```ssh -N -L 1234:[RDS endpoint url]:3306 ec2-user@[ec2 IP address] -i [path to ec2 key]```
* Open a connection in MySQL workbench on 127.0.0.1 and port 1234. Use the master user and password you created.
* Create 'production' and 'test' schemas. Don't add any tables yet.
* Assemble your `DEEPFAKE_DATABASE_STRING` variable. For your development machine this sould look like so: ```mysql://[master user]:[master pw]@127.0.0.1:1234/[test schema name]?charset=utf8```
* Run [db_queries.py](./cogs/db_queries.py) to create the tables.
* Check that the tables are there in MySQL workbench then repeat for the production schema. 

### S3

* Create a private bucket with a policy where objects expire every 24 hours. Change the name in [config.py](./cogs/config.py).
* Create another bucket with no expiration policy. Change the `my_bucket` variable in [build_layer.sh](./lambdas/build_layer.sh).
* Create an IAM user with full permissions to these. Save the credentials to the `DEEPFAKE_AWS_ACCESS_KEY_ID` and `DEEPFAKE_SECRET_ACCESS_KEY` environment variables.

### Elastic Beanstalk

* Provision a Docker worker environment in your public subnet.
* Add the needed EC2 security groups so it can reach the database.
* Create an IAM instance profile.
* Head over to https://discordapp.com/developers and create an app for your bot. Grab its token. While you're at it, create another app for testing.
* Add the following environment variables:
    * `DEEPFAKE_AWS_ACCESS_KEY_ID`
    * `DEEPFAKE_DISCORD_TOKEN`
    * `DEEPFAKE_SECRET_ACCESS_KEY`
    * `DEEPFAKE_DATABASE_STRING` - this should look like so: ```mysql://[master user]:[master pw]@[RDS endpoint url]:3306/[production schema name]?charset=utf8```

### Lambda Functions

* From an EC2 instance, clone the project and run [build_layer.sh](./lambdas/build_layer.sh) to gather the python libraries. This will copy them to your permanent S3 container. Create a Lambda layer from this.
* Create three python lamba functions from [activity](./lambdas/activity/), [markovify](./lambdas/markovify/) and [wordcloud](./lambas/wordcloud/) using your layer. You'll need to give them new names. Then add these names to [config.py](./cogs/config.py).
* Give your EBS's IAM instance profile permission to run them.
* Lambda functions should run in the private subnet. 

### Testing 

* Setup your IDE. I use pycharm, Anaconda, and [this](https://plugins.jetbrains.com/plugin/7861-envfile/) to manage environment variables. You may want to use a different `DEEPFAKE_DISCORD_TOKEN` and `DEEPFAKE_DATABASE_STRING` locally than in EBS. 
* With the SSH tunnel to your database open, run [bot.py](bot.py). Try out all of the bot commands.
* There are unit tests in the [test](./test/) folder but there is no CI setup. The release script will work regardless of whether the tests pass or not.

### Release

* Run [release.sh](release.sh)
* Grab [deploy.zip](deploy.zip) and 'Upload and Deploy' it to EBS.
