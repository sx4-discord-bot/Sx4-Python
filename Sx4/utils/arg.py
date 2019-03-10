import discord
import re

regex_mention = re.compile("<@(?:!|)(\d+)>")
regex_namediscrim = re.compile("(.{2,32})#(\d{4})")
regex_id = re.compile("(^\d+$)")
regex_name = re.compile("(.{2,32})")
role_mention = re.compile("<@&(\d+)>")
channel_mention = re.compile("<#(\d+)>")

async def get_member_info(ctx, user_arg):
    bot = ctx.bot
    match_mention = regex_mention.match(user_arg)
    match_namediscrim = regex_namediscrim.match(user_arg)
    match_id = regex_id.match(user_arg)
    match_name = regex_name.match(user_arg)
    if match_mention:
        id = int(match_mention.group(1))
        user = ctx.guild.get_member(id)
        if not user:
            try:
                user = {x.id: x for x in bot.get_all_members()}[id]
            except KeyError:
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
        id = int(match_id.group(1))
        user = ctx.guild.get_member(id)
        if not user:
            try:
                user = {x.id: x for x in bot.get_all_members()}[id]
            except KeyError:
                try:
                    user = await bot.get_user_info(id)
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

async def get_member(ctx, user_arg):
    bot = ctx.bot
    match_mention = regex_mention.match(user_arg)
    match_namediscrim = regex_namediscrim.match(user_arg)
    match_id = regex_id.match(user_arg)
    match_name = regex_name.match(user_arg)
    if match_mention:
        id = int(match_mention.group(1))
        user = ctx.guild.get_member(id)
        if not user:
            user = bot.get_user(id)
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
                user = [x for x in bot.users if x.name.lower() == name.lower() and x.discriminator == discrim][0]
            except IndexError: 
                return None
    elif match_id:
        id = int(match_id.group(1))
        user = ctx.guild.get_member(id)
        if not user:
            user = bot.get_user(id)
            if not user:
                try:
                    user = await bot.get_user_info(id)
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
                    user = [x for x in bot.users if x.name.lower() == name2.lower()][0]
                except IndexError:
                    return None
    else:
        return None
    return user

def get_role(ctx, role):
    if role_mention.match(role):
        role = ctx.guild.get_role(int(role_mention.match(role).group(1)))
    elif regex_id.match(role):
        role = ctx.guild.get_role(int(regex_id.match(role).group(1)))
    else:
        try:
            role = list(filter(lambda x: x.name.lower() == role.lower(), ctx.guild.roles))[0]
        except IndexError:
            try:
                role = list(filter(lambda x: x.name.lower().startswith(role.lower()), ctx.guild.roles))[0]
            except IndexError:
                try:
                    role = list(filter(lambda x: role.lower() in x.name.lower(), ctx.guild.roles))[0]
                except IndexError:
                    return None
    return role

def get_server_member(ctx, user):
    match_mention = regex_mention.match(user)
    match_namediscrim = regex_namediscrim.match(user)
    match_id = regex_id.match(user)
    match_name = regex_name.match(user)
    if match_mention:
        id = int(match_mention.group(1))
        user = ctx.guild.get_member(id)
        if not user:
            return None
    elif match_namediscrim:
        name = match_namediscrim.group(1)
        discrim = match_namediscrim.group(2)
        try:
            user = [x for x in ctx.guild.members if x.name.lower() == name.lower() and x.discriminator == discrim][0]
        except IndexError:
            return None
    elif match_id:
        id = int(match_id.group(1))
        user = ctx.guild.get_member(id)
        if not user:
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
                    user = [x for x in ctx.guild.members if name2.lower() in x.display_name.lower()][0]
                except IndexError:
                    try:
                        user = [x for x in ctx.guild.members if name2.lower() in x.name.lower()][0]
                    except IndexError:
                        return None
    else:
        return None
    return user

def get_text_channel(ctx, channel):
    if channel_mention.match(channel):
        channel = discord.utils.get(ctx.guild.text_channels, id=int(channel_mention.match(channel).group(1)))
    elif regex_id.match(channel):
        channel = discord.utils.get(ctx.guild.text_channels, id=int(regex_id.match(channel).group(1)))
    else:
        try:
            channel = list(filter(lambda x: x.name.lower() == channel.lower(), ctx.guild.text_channels))[0]
        except IndexError:
            try:
                channel = list(filter(lambda x: x.name.lower().startswith(channel.lower()), ctx.guild.text_channels))[0]
            except IndexError:
                try:
                    channel = list(filter(lambda x: channel.lower() in x.name.lower(), ctx.guild.text_channels))[0]
                except IndexError:
                    return None
    return channel

def get_voice_channel(ctx, channel):
    if regex_id.match(channel):
        channel = discord.utils.get(ctx.guild.voice_channels, id=int(regex_id.match(channel).group(1)))
    else:
        try:
            channel = list(filter(lambda x: x.name.lower() == channel.lower(), ctx.guild.voice_channels))[0]
        except IndexError:
            try:
                channel = list(filter(lambda x: x.name.lower().startswith(channel.lower()), ctx.guild.voice_channels))[0]
            except IndexError:
                try:
                    channel = list(filter(lambda x: channel.lower() in x.name.lower(), ctx.guild.voice_channels))[0]
                except IndexError:
                    return None
    return channel

def get_category(ctx, category):
    if regex_id.match(category):
        channel = discord.utils.get(ctx.guild.categories, id=int(regex_id.match(category).group(1)))
    else:
        try:
            channel = list(filter(lambda x: x.name.lower() == category.lower(), ctx.guild.categories))[0]
        except IndexError:
            try:
                channel = list(filter(lambda x: x.name.lower().startswith(category.lower()), ctx.guild.categories))[0]
            except IndexError:
                try:
                    channel = list(filter(lambda x: category.lower() in x.name.lower(), ctx.guild.categories))[0]
                except IndexError:
                    return None
    return channel