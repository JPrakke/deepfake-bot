# DeepfakeBot

Make copies of your friends! Using the magic of cloud computing, [markov](https://github.com/jsvine/markovify) chains and a little data analytics, you can create a bot that sounds like another discord user.

## Users

[Add](https://discordapp.com/oauth2/authorize?client_id=551871268090019945&scope=bot&permissions=117760) the bot to your discord server. Then go [read](https://deepfake-bot.readthedocs.io/) about how to use it.

## Developers

This is meant to be a rough outline of the steps and AWS resources needed to get this project up and running. It is not a precise how-to as I'm probably forgetting one or more steps. If you're a normal user ready deploy your bot, skip this and see [here](https://deepfake-bot.readthedocs.io/en/latest/self-deployments.html) instead.

### VPC

Setup a VPC with public and private subnets. Traffic on port 3306 should be allowed between them.

### Database

1. Provision a MySQL RDS instance in one of your private subnets. Create a master user and password.
2. Provision an EC2 instance in one of your public subnets.
3. Use an SSH tunnel to this to enable a database connection from a terminal in your development environment: ```ssh -N -L 1234:[RDS endpoint url]:3306 ec2-user@[ec2 IP address] -i [path to ec2 key]```

4. Open a connection in MySQL workbench on 127.0.0.1 and port 1234. Use the master user and password you created.

5. Create 'production' and 'test' schemas.

6. Assemble your `DEEPFAKE_DATABASE_STRING` variable. For your local development environment this sould look like so: ```mysql://[master user]:[master pw]@127.0.0.1:1234/[test schema name]?charset=utf8```

7. Run [db_queries.py](./cogs/db_queries.py) to create the tables.

8. Check that the tables are there in MySQL workbench then repeat for the production schema. 

### S3

1. Create a private bucket with a policy where objects expire every 24 hours. Change the name in [config.py](./cogs/config.py).

2. Create another bucket with no expiration policy. Change the `my_bucket` variable in [build_layer.sh](./lambdas/build_layer.sh).

3. Create an IAM user with full permissions to these. Save the credentials to the `DEEPFAKE_AWS_ACCESS_KEY_ID` and `DEEPFAKE_SECRET_ACCESS_KEY` environment variables.

### Elastic Beanstalk

1. Provision a Docker worker environment in your public subnet.

2. Add the needed EC2 security groups so it can reach the database.

3. Create an IAM instance profile.

4. Head over to https://discordapp.com/developers and create an app for your bot. Grab its token. While you're at it, create another app for testing.

5. Add the following environment variables:

    * `DEEPFAKE_AWS_ACCESS_KEY_ID`
    * `DEEPFAKE_DISCORD_TOKEN`
    * `DEEPFAKE_SECRET_ACCESS_KEY`
    * `DEEPFAKE_DATABASE_STRING` - this should look like so: ```mysql://[master user]:[master pw]@[RDS endpoint url]:3306/[production schema name]?charset=utf8```

### Lambas

1. From an EC2 instance, clone the project and run [build_layer.sh](./lambdas/build_layer.sh) to gather the python libraries. This will copy them to your permanent S3 container. Create a Lambda layer from this.

2. Create three python lamba functions from [activity](./lambdas/activity/), [markovify](./lambdas/markovify/) and [wordcloud](./lambas/wordcloud/) using your layer. You'll need to give them new names. Then add these names to [config.py](./cogs/config.py).

3. Give your EBS's IAM instance profile permission to run them.

### Testing 

1. Setup your IDE. I use pycharm, Anaconda, and [this](https://plugins.jetbrains.com/plugin/7861-envfile/) to manage environment variables. You may want to use a different `DEEPFAKE_DISCORD_TOKEN` and `DEEPFAKE_DATABASE_STRING` locally than in EBS. 

2. With the SSH tunnel to your database open, run [bot.py](bot.py). Try out all of the bot commands.

### Release

1. Run [release.sh](release.sh)

2. Grab [deploy.zip](deploy.zip) and 'Upload and Deploy' it to EBS.
