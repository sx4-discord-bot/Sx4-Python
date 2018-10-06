import discord
import re

regex_mention = re.compile("<@(?:!|)([0-9]+)>")
regex_namediscrim = re.compile("(.{2,32})#([0-9]{4})")
regex_id = re.compile("([0-9]+)")
regex_name = re.compile("(.{2,32})")

async def get_member(bot, ctx, user_arg):
    match_mention = regex_mention.match(user_arg)
    match_namediscrim = regex_namediscrim.match(user_arg)
    match_id = regex_id.match(user_arg)
    match_name = regex_name.match(user_arg)
    if match_mention:
        id = int(match_mention.group(1))
        user = discord.utils.get(ctx.guild.members, id=id)
        if not user:
            user = discord.utils.get(bot.get_all_members(), id=id)
            if not user:
                try:
                    user = await bot.get_user_info(id)
                except:
                    return None
    elif match_namediscrim:
        name = match_namediscrim.group(1)
        discrim = match_namediscrim.group(2)
        try:
            user = [x for x in ctx.guild.members if x.name.lower() == name.lower() and x.discriminator == discrim][0]
        except IndexError:
            try:
                user = [x for x in bot.get_all_members() if x.name.lower() == name.lower() and x.discriminator == discrim][0]
            except IndexError: 
                return None
    elif match_id:
        id2 = int(match_id.group(1))
        user = discord.utils.get(ctx.guild.members, id=id2)
        if not user:
            user = discord.utils.get(bot.get_all_members(), id=id2)
            if not user:
                try:
                    user = await bot.get_user_info(id2)
                except:
                    return None
    elif match_name:
        name2 = match_name.group(1)
        try:
            user = [x for x in ctx.guild.members if x.display_name.lower() == name2.lower()][0]
        except IndexError:
            try:
                user = [x for x in ctx.guild.members if x.name.lower() == name2.lower()][0]
            except IndexError:
                try:
                    user = [x for x in bot.get_all_members() if x.name.lower() == name2.lower()][0]
                except IndexError:
                    return None
    else:
        return None
    return user