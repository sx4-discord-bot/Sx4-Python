import discord
import asyncio
from discord.ext import commands
from random import choice as randchoice
import time
from datetime import datetime
from utils import checks
from urllib.parse import urlencode
from urllib.request import Request, urlopen
import requests
from utils import Token
import inspect
import logging
import aiohttp
import json
from cogs import owner as dev
import rethinkdb as r
import traceback
import sys
import os
import subprocess
   
bot = commands.AutoShardedBot(command_prefix="s??", case_insensitive=False, fetch_offline_members=False)
logging.basicConfig(level=logging.INFO)

@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name + '#' + str(bot.user.discriminator) + ' (' + str(bot.user.id) + ')')
    print('Connected to {} servers and {} users | {} shards'.format(len(bot.guilds), len(set(bot.get_all_members())), bot.shard_count))
    print('------')
    try:
        r.db_create("sx4").run()
    except:
        pass
    r.connect(db="sx4").repl()

@bot.event
async def on_command_error(ctx, error, *args, **kwargs):
    channel = ctx.channel
    author = ctx.author 
    if isinstance(error, commands.CommandNotFound): 
        pass

@bot.event
async def on_message_delete(message):
    author = message.author
    server = message.guild
    serverdata = r.table("logs").get(str(server.id)).run(durability="soft")
    if not serverdata:
        return
    if serverdata["toggle"] == False:
        return
    channel = message.channel
    s=discord.Embed(description="The message sent by **{}** was deleted in <#{}>".format(author.name, channel.id), colour=0xf84b50, timestamp=datetime.utcnow())
    s.set_author(name=author, icon_url=author.avatar_url)
    s.add_field(name="Message", value=message.content)
    await webhook_send(server.get_channel(int(serverdata["channel"])), s)

@bot.event		
async def on_message_edit(before, after):
    author = before.author
    server = before.guild
    serverdata = r.table("logs").get(str(server.id)).run(durability="soft")
    if not serverdata:
        return
    if serverdata["toggle"] == False:
        return
    channel = before.channel
    if before.content == after.content:
        return
    s=discord.Embed(description="{} edited their message in <#{}>".format(author.name, channel.id), colour=0xe6842b, timestamp=datetime.utcnow())
    s.set_author(name=author, icon_url=author.avatar_url)
    s.add_field(name="Before", value=before.content, inline=False)
    s.add_field(name="After", value=after.content)
    await webhook_send(server.get_channel(int(serverdata["channel"])), s)

@bot.event		
async def on_guild_channel_delete(channel):
    server = channel.guild
    deletedby = "Unknown"
    serverdata = r.table("logs").get(str(server.id)).run(durability="soft")
    if not serverdata:
        return
    if serverdata["toggle"] == False:
        return
    for x in await server.audit_logs(limit=100, action=discord.AuditLogAction.channel_delete).flatten():
        if x.target.id == channel.id:
            deletedby = x.user
            break
    if isinstance(channel, discord.TextChannel):
        s=discord.Embed(description="The text channel **{}** has just been deleted by **{}**".format(channel, deletedby), colour=0xf84b50, timestamp=datetime.utcnow())
        s.set_author(name=server, icon_url=server.icon_url)
    elif isinstance(channel, discord.VoiceChannel):
        s=discord.Embed(description="The voice channel **{}** has just been deleted by **{}**".format(channel, deletedby), colour=0xf84b50, timestamp=datetime.utcnow())
        s.set_author(name=server, icon_url=server.icon_url)
    else:
        s=discord.Embed(description="The category **{}** has just been deleted by **{}**".format(channel, deletedby), colour=0xf84b50, timestamp=datetime.utcnow())
        s.set_author(name=server, icon_url=server.icon_url)
    await webhook_send(server.get_channel(int(serverdata["channel"])), s)

@bot.event		
async def on_guild_channel_create(channel):
    server = channel.guild
    createdby = "Unknown"
    serverdata = r.table("logs").get(str(server.id)).run(durability="soft")
    if not serverdata:
        return
    if serverdata["toggle"] == False:
        return
    for x in await server.audit_logs(limit=100, action=discord.AuditLogAction.channel_create).flatten():
        if x.target.id == channel.id:
            createdby = x.user
            break
    if isinstance(channel, discord.TextChannel):
        s=discord.Embed(description="The text channel <#{}> has just been created by **{}**".format(channel.id, createdby), colour=0x5fe468, timestamp=datetime.utcnow())
        s.set_author(name=server, icon_url=server.icon_url)
    elif isinstance(channel, discord.VoiceChannel):
        s=discord.Embed(description="The voice channel **{}** has just been created by **{}**".format(channel, createdby), colour=0x5fe468, timestamp=datetime.utcnow())
        s.set_author(name=server, icon_url=server.icon_url)
    else:
        s=discord.Embed(description="The category **{}** has just been created by **{}**".format(channel, createdby), colour=0x5fe468, timestamp=datetime.utcnow())
        s.set_author(name=server, icon_url=server.icon_url)
    await webhook_send(server.get_channel(int(serverdata["channel"])), s)

@bot.event		
async def on_guild_channel_update(before, after):
    server = before.guild
    editedby = "Unknown"
    serverdata = r.table("logs").get(str(server.id)).run(durability="soft")
    if not serverdata:
        return
    if serverdata["toggle"] == False:
        return
    if isinstance(before, discord.TextChannel):
        if before.name != after.name:
            for x in await server.audit_logs(limit=100, action=discord.AuditLogAction.channel_update).flatten():
                if x.target.id == after.id:
                    editedby = x.user
                    break
            s=discord.Embed(description="The text channel <#{}> has been renamed by **{}**".format(after.id, editedby), colour=0xe6842b, timestamp=datetime.utcnow())
            s.set_author(name=server, icon_url=server.icon_url)
            s.add_field(name="Before", value="`{}`".format(before))
            s.add_field(name="After", value="`{}`".format(after))
        if before.slowmode_delay != after.slowmode_delay:
            for x in await server.audit_logs(limit=1).flatten():
                if x.action == discord.AuditLogAction.channel_update:
                    editedby = x.user
            s=discord.Embed(description="The slowmode in {} has been changed by **{}**".format(after.mention, editedby), colour=0xe6842b, timestamp=datetime.utcnow())
            s.set_author(name=server, icon_url=server.icon_url)
            s.add_field(name="Before", value="{} {}".format(before.slowmode_delay, "second" if before.slowmode_delay == 1 else "seconds") if before.slowmode_delay != 0 else "Disabled")
            s.add_field(name="After", value="{} {}".format(after.slowmode_delay, "second" if after.slowmode_delay == 1 else "seconds") if after.slowmode_delay != 0 else "Disabled")
    elif isinstance(before, discord.VoiceChannel):
        if before.name != after.name:
            for x in await server.audit_logs(limit=100, action=discord.AuditLogAction.channel_update).flatten():
                if x.target.id == after.id:
                    editedby = x.user
                    break
            s=discord.Embed(description="The voice channel **{}** has been renamed by **{}**".format(after, editedby), colour=0xe6842b, timestamp=datetime.utcnow())
            s.set_author(name=server, icon_url=server.icon_url)
            s.add_field(name="Before", value="`{}`".format(before))
            s.add_field(name="After", value="`{}`".format(after))
    else:
        if before.name != after.name:
            for x in await server.audit_logs(limit=100, action=discord.AuditLogAction.channel_update).flatten():
                if x.target.id == after.id:
                    editedby = x.user
                    break
            s=discord.Embed(description="The category **{}** has been renamed by **{}**".format(after, editedby), colour=0xe6842b, timestamp=datetime.utcnow())
            s.set_author(name=server, icon_url=server.icon_url)
            s.add_field(name="Before", value="`{}`".format(before))
            s.add_field(name="After", value="`{}`".format(after))
    await webhook_send(server.get_channel(int(serverdata["channel"])), s)

@bot.event		
async def on_member_join(member):
    server = member.guild
    serverdata = r.table("logs").get(str(server.id)).run(durability="soft")
    if not serverdata:
        return
    if serverdata["toggle"] == False:
        return
    s=discord.Embed(description="**{}** just joined the server".format(member.name), colour=0x5fe468, timestamp=datetime.utcnow())
    s.set_author(name=member, icon_url=member.avatar_url)
    s.set_footer(text="User ID: {}".format(member.id))
    await webhook_send(server.get_channel(int(serverdata["channel"])), s)

@bot.event	 
async def on_member_remove(member):
    server = member.guild
    serverdata = r.table("logs").get(str(server.id)).run(durability="soft")
    if not serverdata:
        return
    if serverdata["toggle"] == False:
        return
    s=discord.Embed(description="**{}** just left the server".format(member.name), colour=0xf84b50, timestamp=datetime.utcnow())
    s.set_author(name=member, icon_url=member.avatar_url)
    s.set_footer(text="User ID: {}".format(member.id))
    await webhook_send(server.get_channel(int(serverdata["channel"])), s)

@bot.event	
async def on_member_ban(guild, user):
    await asyncio.sleep(0.5)
    server = guild
    serverdata = r.table("logs").get(str(server.id)).run(durability="soft")
    if not serverdata:
        return
    if serverdata["toggle"] == False:
        return
    moderator = "Unknown"
    for x in await server.audit_logs(limit=100, action=discord.AuditLogAction.ban).flatten():
        if x.target == user:
            moderator = x.user
            break
    s=discord.Embed(description="**{}** has been banned by **{}**".format(user.name, moderator), colour=0xf84b50, timestamp=datetime.utcnow())
    s.set_author(name=user, icon_url=user.avatar_url)
    s.set_footer(text="User ID: {}".format(user.id))
    await webhook_send(server.get_channel(int(serverdata["channel"])), s)

@bot.event	
async def on_member_unban(guild, user):
    await asyncio.sleep(0.5)
    server = guild
    serverdata = r.table("logs").get(str(server.id)).run(durability="soft")
    if not serverdata:
        return
    if serverdata["toggle"] == False:
        return
    moderator = "Unknown"
    for x in await server.audit_logs(limit=100, action=discord.AuditLogAction.unban).flatten():
        if x.target == user:
            moderator = x.user
            break
    s=discord.Embed(description="**{}** has been unbanned by **{}**".format(user.name, moderator), colour=0x5fe468, timestamp=datetime.utcnow())
    s.set_author(name=user, icon_url=user.avatar_url)
    s.set_footer(text="User ID: {}".format(user.id))
    await webhook_send(server.get_channel(int(serverdata["channel"])), s)

@bot.event	
async def on_guild_role_create(role): 
    server = role.guild
    serverdata = r.table("logs").get(str(server.id)).run(durability="soft")
    if not serverdata:
        return
    if serverdata["toggle"] == False:
        return
    user = "Unknown"
    for x in await server.audit_logs(limit=100, action=discord.AuditLogAction.role_create).flatten():
        if x.target.id == role.id:
            user = x.user
            break
    s=discord.Embed(description="The role **{}** has been created by **{}**".format(role.name, user), colour=0x5fe468, timestamp=datetime.utcnow())
    s.set_author(name=server, icon_url=server.icon_url)
    await webhook_send(server.get_channel(int(serverdata["channel"])), s)

@bot.event		 
async def on_guild_role_delete(role):
    server = role.guild
    serverdata = r.table("logs").get(str(server.id)).run(durability="soft")
    if not serverdata:
        return
    if serverdata["toggle"] == False:
        return
    user = "Unknown"
    for x in await server.audit_logs(limit=100, action=discord.AuditLogAction.role_delete).flatten():
        if x.target.id == role.id:
            user = x.user
            break
    s=discord.Embed(description="The role **{}** has been deleted by **{}**".format(role.name, user), colour=0xf84b50, timestamp=datetime.utcnow())
    s.set_author(name=server, icon_url=server.icon_url)
    await webhook_send(server.get_channel(int(serverdata["channel"])), s)

@bot.event	
async def on_guild_role_update(before, after):
    server = before.guild
    user = "Unknown"
    serverdata = r.table("logs").get(str(server.id)).run(durability="soft")
    if not serverdata:
        return
    if serverdata["toggle"] == False:
        return
    for x in await server.audit_logs(limit=100, action=discord.AuditLogAction.role_update).flatten():
        if x.target.id == after.id:
            user = x.user
            break
    if before.name != after.name:
        s=discord.Embed(description="The role **{}** has been renamed by **{}**".format(before.name, user), colour=0xe6842b, timestamp=datetime.utcnow())
        s.set_author(name=server, icon_url=server.icon_url)
        s.add_field(name="Before", value=before)
        s.add_field(name="After", value=after)
    elif before.permissions != after.permissions:
        permissionadd = list(map(lambda x: "+ " + x[0].replace("_", " ").title(), filter(lambda x: x[0] in map(lambda x: x[0], filter(lambda x: x[1] == True, after.permissions)), filter(lambda x: x[1] == False, before.permissions))))
        permissionremove = list(map(lambda x: "- " + x[0].replace("_", " ").title(), filter(lambda x: x[0] in map(lambda x: x[0], filter(lambda x: x[1] == False, after.permissions)), filter(lambda x: x[1] == True, before.permissions))))
        s=discord.Embed(description="The role **{}** has had permission changes made by **{}**\n```diff\n{}\n{}```".format(before.name, user, "\n".join(permissionadd), "\n".join(permissionremove)), colour=0xe6842b, timestamp=datetime.utcnow())
        s.set_author(name=server, icon_url=server.icon_url)
    else: 
        return
    await webhook_send(server.get_channel(int(serverdata["channel"])), s)

@bot.event		
async def on_voice_state_update(member, before, after):
    server = member.guild
    serverdata = r.table("logs").get(str(server.id)).run(durability="soft")
    if not serverdata:
        return
    if serverdata["toggle"] == False:
        return
    action = "Unknown"
    if after.channel == None:
        s=discord.Embed(description="**{}** just left the voice channel `{}`".format(member.name, before.channel), colour=0xf84b50, timestamp=datetime.utcnow())
        s.set_author(name=member, icon_url=member.avatar_url)
    elif before.channel == None:
        s=discord.Embed(description="**{}** just joined the voice channel `{}`".format(member.name, after.channel), colour=0x5fe468, timestamp=datetime.utcnow())
        s.set_author(name=member, icon_url=member.avatar_url)
    elif before.channel != after.channel:
        s=discord.Embed(description="**{}** just changed voice channels".format(member.name), colour=0xe6842b, timestamp=datetime.utcnow())
        s.set_author(name=member, icon_url=member.avatar_url)
        s.add_field(name="Before", value="`{}`".format(before.channel), inline=False)
        s.add_field(name="After", value="`{}`".format(after.channel))
    elif before.mute and not after.mute:
        for x in await server.audit_logs(limit=100, action=discord.AuditLogAction.member_update).flatten():
            if x.target.id == member.id:
                action = x.user
                break
        s=discord.Embed(description="**{}** has been unmuted by **{}**".format(member.name, action), colour=0x5fe468, timestamp=datetime.utcnow())
        s.set_author(name=member, icon_url=member.avatar_url)
    elif not before.mute and after.mute:
        for x in await server.audit_logs(limit=100, action=discord.AuditLogAction.member_update).flatten():
            if x.target.id == member.id:
                action = x.user
                break
        s=discord.Embed(description="**{}** has been muted by **{}**".format(member.name, action), colour=0xf84b50, timestamp=datetime.utcnow())
        s.set_author(name=member, icon_url=member.avatar_url)
    elif before.deaf and not after.deaf:
        for x in await server.audit_logs(limit=100, action=discord.AuditLogAction.member_update).flatten():
            if x.target.id == member.id:
                action = x.user
                break
        s=discord.Embed(description="**{}** has been undeafened by **{}**".format(member.name, action), colour=0x5fe468, timestamp=datetime.utcnow())
        s.set_author(name=member, icon_url=member.avatar_url)
    elif not before.deaf and after.deaf:
        for x in await server.audit_logs(limit=100, action=discord.AuditLogAction.member_update).flatten():
            if x.target.id == member.id:
                action = x.user
                break
        s=discord.Embed(description="**{}** has been deafened by **{}**".format(member.name, action), colour=0xf84b50, timestamp=datetime.utcnow())
        s.set_author(name=member, icon_url=member.avatar_url)
    else:
        return
    await webhook_send(server.get_channel(int(serverdata["channel"])), s)

@bot.event	
async def on_member_update(before, after):
    server = before.guild
    serverdata = r.table("logs").get(str(server.id)).run(durability="soft")
    if not serverdata:
        return
    if serverdata["toggle"] == False:
        return
    user = "Unknown"
    if before.roles != after.roles:
        for x in await server.audit_logs(limit=100, action=discord.AuditLogAction.member_role_update).flatten():
            if x.target == after:
                user = x.user
                break
        for role in before.roles:
            if role not in after.roles:
                s=discord.Embed(description="The role `{}` has been removed from **{}** by **{}**".format(role, after.name, user), colour=0xf84b50, timestamp=datetime.utcnow())
                s.set_author(name=after, icon_url=before.avatar_url)
        for role in after.roles:
            if role not in before.roles:
                s=discord.Embed(description="The role `{}` has been added to **{}** by **{}**".format(role, after.name, user), colour=0x5fe468, timestamp=datetime.utcnow())
                s.set_author(name=after, icon_url=before.avatar_url)
    elif before.nick != after.nick:
        for x in await server.audit_logs(limit=100, action=discord.AuditLogAction.member_update).flatten():
            if x.target.id == after.id:
                user = x.user
                break
        if not before.nick:
            before.nick = after.name
        if not after.nick:
            after.nick = after.name
        s=discord.Embed(description="**{}** has had their nickname changed by **{}**".format(after.name, user), colour=0xe6842b, timestamp=datetime.utcnow())
        s.set_author(name=after, icon_url=after.avatar_url)
        s.add_field(name="Before", value=before.nick, inline=False)
        s.add_field(name="After", value=after.nick)
    else:
        return
    await webhook_send(server.get_channel(int(serverdata["channel"])), s)

async def webhook_send(channel, embed):
    try:
        with open("sx4-byellow.png", "rb") as f:
            avatar = f.read()
    except:
        avatar = None
    webhooks = await channel.webhooks()
    webhook = discord.utils.get(webhooks, name="Sx4 - Logs")
    if not webhook:
        webhook = await channel.create_webhook(name="Sx4 - Logs", avatar=avatar)
    await webhook.send(embed=embed)	
        	
class Main:
    def __init__(self, bot):
        self.bot = bot

@bot.command()
@checks.is_owner()
async def parse(ctx, *, code: str=None):
    if not code:
        code = requests.get(ctx.message.attachments[0].url).content.decode()
    code = "    " + code.replace("\n", "\n    ")
    code = "async def __eval_function__():\n" + code

    additional = {}
    additional["ctx"] = ctx
    additional["channel"] = ctx.channel
    additional["author"] = ctx.author
    additional["guild"] = ctx.guild

    try:
        exec(code, {**globals(), **additional}, locals())

        await locals()["__eval_function__"]()
    except Exception as e:
        await ctx.send(str(e))
            
@bot.command(name="eval")
@checks.is_owner()
async def _eval(ctx, *, code):
    author = ctx.author
    server = ctx.guild
    channel = ctx.channel
    try:
        await ctx.send(str(await eval(code))) 
    except:
        try:
            await ctx.send(str(eval(code))) 
        except Exception as e:
            await ctx.send(str(e))
		
bot.add_cog(Main(bot))

bot.remove_command('help')

bot.run(Token.bot())
