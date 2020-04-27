Change Log
==========

Releases
--------

1.2.2
`````
* Made all commands respond with 'Usage' message if the wrong arguments are given
* Added a link to Model Tuning documentation when model generation fails
* Made auto filters be at least two characters long

1.2.1
`````
* Added ``impersonate`` command to DeepfakeBot
* Bug fixes to ``extract`` and ``filter`` commands

1.2.0
`````
* Added a message to new users with a link to documentation
* Training subjects are now linked to trainers - i.e. other users can't mess with your filters or model settings
* Changed S3 expiration time to 30 days
* Added auto filters for extract task, added direct message when extraction task finishes
* Added ``newsletter`` command
* Added cooldowns to commands
* Documentation updates: added interacting-with-your-bot page, added notes for Plexi users, added changelog
* self-deployment branch: Renamed "generate" to "impersonate" for your bot
* self-deployment branch: Config settings change also updates .json file in S3 
* self-deployment branch: Added catfacts, catpics, and asciify commands

1.1.0
`````
* Fixed an issue with the extract task related to anmiated emojis by updating Discord.py version
* Added a message with a time estimate for extract task
* Added only a single extract task per user at once

1.0.7
`````
* Big documentation update
* Default config changes: removed 'favorite words', added owner_id

1.0.6
`````
* Moved avatar url to private message
* Fixed an issue with activity plots
* Added avatar url to deploy self
* Added user name to message when markov model generator fails

1.0.5
`````
* Added generate command
* Made lambda invokations asynchronous
* Added timestamps to logging
* Added a stats command
* Updated readme
* Documentation setup
* Changed activity plot to use user.name instead of nick

1.0.4
`````
* Moved activity plot to lambda function, added a lambda cog base class
* Extract improvements: added better handling of mentions, renamed channels csv file

1.0.3
`````
* Removed unique constraint on subjects table
* Made wordcloud a lambda function, added a lambda layer

1.0.2
`````
* Release script setup

1.0.1
`````
* Release script setup

1.0.0
`````
* First stable release using Markov chains
