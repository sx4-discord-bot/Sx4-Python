import discord
import asyncio
from discord.ext import commands
from random import choice as randchoice
import time
import datetime
from utils.dataIO import dataIO
from utils import checks
from urllib.parse import urlencode
from urllib.request import Request, urlopen
import requests
from cogs.mod import Prefix
import aiohttp
import json
import traceback
import sys
import os
import subprocess


async def prefix_function(bot, message):
    try:
        return [x.encode().decode() for x in Prefix._prefixes["userprefix"][str(message.author.id)]] + ['<@440996323156819968> ']
    except:
        pass
    try:
        return [x.encode().decode() for x in Prefix._prefixes["serverprefix"][str(message.guild.id)]] + ['<@440996323156819968> ']
    except:
        pass
    return ['sx4 ', 's?', 'S?', '<@440996323156819968> ']
   
bot = commands.AutoShardedBot(command_prefix=prefix_function)
wrap = "```py\n{}\n```"
dbltoken = "token"
dbotspwtoken = "token was not found"
botspacetoken = "token.exe has stopped working"
dbpwurl = "https://bots.discord.pw/api/bots/440996323156819968/stats"
url = "https://discordbots.org/api/bots/440996323156819968/stats"
botspaceurl = "https://botlist.space/api/bots/440996323156819968/"
headers = {"Authorization" : dbltoken, "Content-Type" : "application/json"}
headersdb = {"Authorization" : dbotspwtoken, "Content-Type" : "application/json"}
headersbs = {"Authorization" : botspacetoken, "Content-Type" : "application/json"}

modules = ["cogs." + x.replace(".py", "") for x in os.listdir("cogs") if ".py" in x]

@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name + '#' + str(bot.user.discriminator) + ' (' + str(bot.user.id) + ')')
    print('Connected to {} servers and {} users | {} shards'.format(len(bot.guilds), len(set(bot.get_all_members())), bot.shard_count))
    print('------')
    for extension in modules:
        try:
            bot.load_extension(extension)
        except Exception as e:
            print('Failed to load extension {}\n{}: {}'.format(extension, type(e).name, e))
    payloadservers = {"server_count"  : len(bot.guilds)}
    payloadshards = {"shard_count"  : bot.shard_count}
    requests.post(url, data=payloadservers, headers=headers)
    requests.post(url, data=payloadshards, headers=headers)
    requests.post(dbpwurl, data=json.dumps(payloadservers), headers=headersdb)
    requests.post(botspaceurl, data=json.dumps(payloadservers), headers=headersbs)
    if not hasattr(bot, 'uptime'):
        bot.uptime = datetime.datetime.utcnow().timestamp()

@bot.event
async def on_guild_join(guild):
    payloadservers = {"server_count"  : len(bot.guilds)}
    payloadshards = {"shard_count"  : bot.shard_count}
    requests.post(url, data=payloadservers, headers=headers)
    requests.post(url, data=payloadshards, headers=headers)
    requests.post(botspaceurl, data=json.dumps(payloadservers), headers=headersbs)
    requests.post(dbpwurl, data=json.dumps(payloadservers), headers=headersdb)
		
@bot.event 
async def on_message(message):
    if message.author.bot:
        return
    if isinstance(message.channel, discord.abc.PrivateChannel) and message.content.startswith("s?"):
        await message.channel.send("You can't use commands in private messages :no_entry:")
        return
    else:
        await bot.process_commands(message)

@bot.event 
async def on_message_edit(before, after):
    if after.author.bot:
        return
    elif before.content == after.content:
        return
    elif isinstance(after.channel, discord.abc.PrivateChannel) and after.content.startswith("s?"):
        await after.channel.send("You can't use commands in private messages :no_entry:")
        return
    else:
        await bot.process_commands(after)
		
@bot.event
async def on_guild_remove(guild):
    payloadservers = {"server_count"  : len(bot.guilds)}
    payloadshards = {"shard_count"  : bot.shard_count}
    requests.post(url, data=payloadservers, headers=headers)
    requests.post(url, data=payloadshards, headers=headers)
    requests.post(botspaceurl, data=json.dumps(payloadservers), headers=headersbs)
    requests.post(dbpwurl, data=json.dumps(payloadservers), headers=headersdb)
			
@bot.event
async def on_command_error(ctx, error, *args, **kwargs):
    channel = ctx.channel
    author = ctx.author 
    if isinstance(error, commands.CheckFailure):
        return await channel.send("You do not have permission to use this command :no_entry:")
    elif isinstance(error, commands.NoPrivateMessage):
        return await channel.send("This command cannot be used in DMs!")
    elif isinstance(error, commands.DisabledCommand):
        return await channel.send("{} has been disabled!".format(ctx.command))
    elif isinstance(error, commands.CommandOnCooldown):
        m, s = divmod(error.retry_after, 60)
        h, m = divmod(m, 60)
        if h == 0:
            time = "%d minutes %d seconds" % (m, s)
        elif h == 0 and m == 0:
            time = "%d seconds" % (s)
        else:
            time = "%d hours %d minutes %d seconds" % (h, m, s)
        return await channel.send("This command is on cooldown! Try again in {}".format(time))
    elif isinstance(error, commands.MissingRequiredArgument):
        msg = ""
        for x in ctx.command.params:
            if x != "ctx":
                if x != "self":
                    if "None" in str(ctx.command.params[x]):
                        msg += "[{}] ".format(x)
                    else:
                        msg += "<{}> ".format(x)
        if not ctx.command.aliases:
            aliases = "None"
        else:
            aliases = ", ".join([x for x in ctx.command.aliases])
        msg = "Usage: {}{} {}\nCommand aliases: {}\nCommand description: {}".format(ctx.prefix, ctx.command, msg, aliases, ctx.command.help)
        try:
            msg += "\n\nSub commands: {}".format(", ".join([x for x in ctx.command.all_commands if x not in ctx.command.all_commands[x].aliases]))
        except:
            pass
        s=discord.Embed(description=msg)
        s.set_author(name=ctx.command, icon_url=bot.user.avatar_url)
        return await channel.send(embed=s)
    elif isinstance(error, commands.CommandNotFound): 
        pass
    elif isinstance(error, commands.BadArgument):
        msg = ""
        for x in ctx.command.params:
            if x != "ctx":
                if x != "self":
                    if "None" in str(ctx.command.params[x]):
                        msg += "[{}] ".format(x)
                    else:
                        msg += "<{}> ".format(x)
        msg = "Usage: {}{} {}\nCommand description: {}".format(ctx.prefix, ctx.command, msg, ctx.command.help)
        s=discord.Embed(description=msg )
        s.set_author(name=ctx.command, icon_url=bot.user.avatar_url)
        return await channel.send(embed=s)
    else:
        s=discord.Embed(title="Error", description="You have came across an error! [Support Server](https://discord.gg/WJHExmg)\n{}".format(str(error)).replace("Command raised an exception: ", ""))
        await channel.send(embed=s)
        await bot.get_channel(439745234285625355).send("```Server: {}\nTime: {}\nCommand: {}\n\n{}```".format(ctx.message.guild, datetime.datetime.utcnow().strftime("%d/%m/%Y %H:%M:%S"), ctx.command, str(error)))
        print("".join(traceback.format_exception(type(error), error, error.__traceback__)))
        
		
class Main:
    def __init__(self, bot):
        self.bot = bot
		
@bot.command(hidden=True)
@checks.is_owner()
async def load(ctx, *, module: str):
    """loads a part of the bot."""
    m = "cogs." + module
    try:
        if m in modules:
            bot.load_extension(m)
            await ctx.send("The module `{}` has been loaded <:done:403285928233402378>".format(module))
        else:
            await ctx.send("I cannot find the module you want me to load <:crossmark:410105895528300554>")
    except Exception as e:
        e=discord.Embed(description="Error:" + wrap.format(type(e).name + ': ' + str(e)), colour=discord.Colour.red())
        await ctx.send(embed=e)
		
@bot.command(hidden=True)
@checks.is_owner()
async def unload(ctx, *, module: str):
    """unloads a part of the bot."""
    m = "cogs." + module
    try:
        if m in modules:
            bot.unload_extension(m)
            await ctx.send("The module `{}` has been unloaded <:done:403285928233402378>".format(module))
        else:
            await ctx.send("I cannot find the module you want me to unload <:crossmark:410105895528300554>")
    except Exception as e:
        e=discord.Embed(description="Error:" + wrap.format(type(e).name + ': ' + str(e)), colour=discord.Colour.red())
        await ctx.send(embed=e)
		
@bot.command(hidden=True)
@checks.is_owner()
async def reload(ctx, *, module: str):
    """Reloads a part of the bot."""
    if module.lower() == "all":
        i = 0
        for m in modules:
            try:
                bot.unload_extension(m)
                bot.load_extension(m)
            except:
                i += 1
                await ctx.send("I was not able to load the module `{}` <:crossmark:410105895528300554>".format(str(m)[4:]))
        if i == 0:
            await ctx.send("All modules have been reloaded <:done:403285928233402378>")
        else:
            await ctx.send("{} modules have been reloaded <:done:403285928233402378>".format(len(modules)-i))
        return
    m = "cogs." + module
    try:
        if m in modules:
            bot.unload_extension(m)
            bot.load_extension(m)
            await ctx.send("The module `{}` has been reloaded <:done:403285928233402378>".format(module))
        else:
            await ctx.send("I cannot find the module you want me to reload <:crossmark:410105895528300554>")
    except Exception as e:
        e=discord.Embed(description="Error:" + wrap.format(type(e).name + ': ' + str(e)), colour=discord.Colour.red())
        await ctx.send(embed=e)
		
		
bot.add_cog(Main(bot))

bot.run('customstokensareathing')

