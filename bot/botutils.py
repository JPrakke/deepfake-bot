from discord import utils


# Use this to identify a user by mention or name#discriminator
def get_subject(bot, ctx, subject_string):
    mentions = ctx.message.mentions

    if len(mentions) == 1:
        return mentions[0]
    elif len(mentions) > 1:
        return 'Too many...'
    else:
        try:
            subject_name = subject_string.split('#')[0]
            subject_discriminator = subject_string.split('#')[1]
            p = bot.get_all_members()
            found_members = filter(lambda m: (m.discriminator == subject_discriminator)
                                             and (m.name == subject_name), p)

            return utils.get(found_members)

        except IndexError:
            return 'Not found'
