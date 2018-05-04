import discord
import asyncio
from discord.ext import commands
from random import choice as randchoice
import time
import datetime
from utils import checks
import aiohttp
import json
import traceback
import sys
import os
import subprocess

bot = commands.Bot(command_prefix=['sx4 ', 's?', 'S?'], description='Sx4 Bot', pm_help=None) 
wrap = "```py\n{}\n```"
dbltoken = "A Discord bot list token would go here"
url = "https://discordbots.org/api/bots/{bot.id}/stats"
headers = {"Authorization" : dbltoken}

modules = ['cogs.general', 'cogs.status', 'cogs.owner', 'cogs.economy', 'cogs.help', 'cogs.mod', 'cogs.joinleave', 'cogs.antiad', 'cogs.antilink', 'cogs.serverlog', 'cogs.logs', 'cogs.autorole', 'cogs.mention', 'cogs.afk', 'cogs.selfroles', 'cogs.page', 'cogs.music']

@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name + '#' + bot.user.discriminator + ' (' + bot.user.id + ')')
    print('Connected to {} servers and {} users'.format(len(bot.servers), len(set(bot.get_all_members()))))
    print('------')
    os.environ['TZ'] = 'BST'
    time.tzset()
    for extension in modules:
        try:
            bot.load_extension(extension)
        except Exception as e:
            print('Failed to load extension {}\n{}: {}'.format(extension, type(e).name, e))
    payload = {"server_count"  : len(bot.servers)}
    async with aiohttp.ClientSession() as aioclient:
        await aioclient.post(url, data=payload, headers=headers)

@bot.event
async def on_server_join(server):
    payload = {"server_count"  : len(bot.servers)}
    async with aiohttp.ClientSession() as aioclient:
            await aioclient.post(url, data=payload, headers=headers)

@bot.event
async def on_server_remove(server):
    payload = {"server_count"  : len(bot.servers)}
    async with aiohttp.ClientSession() as aioclient:
            await aioclient.post(url, data=payload, headers=headers)
			
@bot.event
async def on_command_error(error, ctx, *args, **kwargs):
    channel = ctx.message.channel
    author = ctx.message.author 
    if isinstance(error, commands.CheckFailure):
        return await bot.send_message(channel, "You do not have permission to use this command :no_entry:")
    elif isinstance(error, commands.NoPrivateMessage):
        return await bot.send_message(channel, "This command cannot be used in DMs!")
    elif isinstance(error, commands.DisabledCommand):
        return await bot.send_message(channel, "{} has been disabled!".format(ctx.command))
    elif isinstance(error, commands.CommandOnCooldown):
        m, s = divmod(error.retry_after, 60)
        h, m = divmod(m, 60)
        if h == 0:
            time = "%d minutes %d seconds" % (m, s)
        elif h == 0 and m == 0:
            time = "%d seconds" % (s)
        else:
            time = "%d hours %d minutes %d seconds" % (h, m, s)
        return await bot.send_message(channel, "This command is on cooldown! Try again in {}".format(time))
    elif isinstance(error, commands.MissingRequiredArgument):
        msg = ""
        for x in ctx.command.params:
            if x != "ctx":
                if x != "self":
                    if "None" in str(ctx.command.params[x]):
                        msg += "[{}] ".format(x)
                    else:
                        msg += "<{}> ".format(x)
        msg = "Usage: {}{} {}\nCommand description: {}".format(ctx.prefix, ctx.command, msg, ctx.command.help)
        s=discord.Embed(description=msg)
        s.set_author(name=ctx.command, icon_url=bot.user.avatar_url)
        return await bot.send_message(channel, embed=s)
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
        return await bot.send_message(channel, embed=s)
    else:
        s=discord.Embed(title="Error", description="You have came across an error! [Support Server](https://discord.gg/WJHExmg)\n{}".format(str(error)).replace("Command raised an exception: ", ""))
        await bot.send_message(channel, embed=s)
        await bot.send_message(bot.get_channel("439745234285625355"), "```Server: {}\nTime: {}\nCommand: {}\n\n{}```".format(ctx.message.server, datetime.datetime.utcnow().strftime("%d/%m/%Y %H:%M:%S"), ctx.command, str(error)))
        print("".join(traceback.format_exception(type(error), error, error.__traceback__)))
        
		
class Main:
    def __init__(self, bot):
        self.bot = bot
		
@bot.command(hidden=True)
@checks.is_owner()
async def load(*, module: str):
    """loads a part of the bot."""
    m = "cogs." + module
    try:
        if m in modules:
            bot.load_extension(m)
            await bot.say("The module `{}` has been loaded <:done:403285928233402378>".format(module))
        else:
            await bot.say("I cannot find the module you want me to load <:crossmark:410105895528300554>")
    except Exception as e:
        e=discord.Embed(description="Error:" + wrap.format(type(e).name + ': ' + str(e)), colour=discord.Colour.red())
        await bot.say(embed=e)
		
@bot.command(hidden=True)
@checks.is_owner()
async def unload(*, module: str):
    """unloads a part of the bot."""
    m = "cogs." + module
    try:
        if m in modules:
            bot.unload_extension(m)
            await bot.say("The module `{}` has been unloaded <:done:403285928233402378>".format(module))
        else:
            await bot.say("I cannot find the module you want me to unload <:crossmark:410105895528300554>")
    except Exception as e:
        e=discord.Embed(description="Error:" + wrap.format(type(e).name + ': ' + str(e)), colour=discord.Colour.red())
        await bot.say(embed=e)
		
@bot.command(hidden=True)
@checks.is_owner()
async def reload(*, module: str):
    """Reloads a part of the bot."""
    m = "cogs." + module
    try:
        if m in modules:
            bot.unload_extension(m)
            bot.load_extension(m)
            await bot.say("The module `{}` has been reloaded <:done:403285928233402378>".format(module))
        else:
            await bot.say("I cannot find the module you want me to reload <:crossmark:410105895528300554>")
    except Exception as e:
        e=discord.Embed(description="Error:" + wrap.format(type(e).name + ': ' + str(e)), colour=discord.Colour.red())
        await bot.say(embed=e)
		
bot.add_cog(Main(bot))

bot.run('Not getting my Token')

