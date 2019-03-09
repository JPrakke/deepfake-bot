from discord import utils


# Use this to identify a user by mention or name#discriminator
def get_subject(bot, ctx, args, command_name):
    mentions = ctx.message.mentions

    if len(args) == 1:
        subject_string = args[0]
    else:
        return False, f'Usage: `df!{command_name} User#0000`'

    if len(mentions) == 1:
        return mentions[0], ''
    elif len(mentions) > 1:
        return False, f'One at a time please. Usage: `df!{command_name} User#0000`'

    else:
        try:
            subject_name = subject_string.split('#')[0]
            subject_discriminator = subject_string.split('#')[1]
            p = bot.get_all_members()
            found_members = filter(lambda m: (m.discriminator == subject_discriminator)
                                   and (m.name == subject_name), p)
            subject =  utils.get(found_members)
            if subject:
                return subject, ''
            else:
                return False, f'Hmmm... I can\'t seem to find {subject_string}'

        except IndexError:
            return False, f'Hmmm... I can\'t seem to find {subject_string}'
