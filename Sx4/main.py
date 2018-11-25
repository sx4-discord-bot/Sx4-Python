import discord
import asyncio
from discord.ext import commands
from random import choice as randchoice
import time
import datetime
from utils import checks
from urllib.parse import urlencode
from urllib.request import Request, urlopen
import requests
from utils import Token
import inspect
import aiohttp
import json
import rethinkdb as r
import traceback
import sys
import os
import subprocess

async def prefix_function(bot, message):
    user = r.table("prefix").get(str(message.author.id)).run()
    server = r.table("prefix").get(str(message.guild.id)).run()
    if user and user["prefixes"] != []:
        return [x.encode().decode() for x in user["prefixes"]] + ['<@440996323156819968> ']
    elif server and server["prefixes"] != []:
        return [x.encode().decode() for x in server["prefixes"]] + ['<@440996323156819968> ']
    else:
        return ['s?', 'S?', 'sx4 ', '<@440996323156819968> ']
   
bot = commands.AutoShardedBot(command_prefix=prefix_function, case_insensitive=False)
wrap = "```py\n{}\n```"
modules = ["cogs." + x.replace(".py", "") for x in os.listdir("cogs") if ".py" in x]

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
    r.table("blacklist").insert({"id": "owner", "users": []}).run()
    for extension in modules:
        try:
            bot.load_extension(extension)
        except Exception as e:
            print(e)
    setattr(bot, "uptime", datetime.datetime.utcnow().timestamp())
		
@bot.event 
async def on_message(message):
    await bot.wait_until_ready()
    ctx = await bot.get_context(message)
    if checks.is_owner_check(ctx):
        return await bot.process_commands(message)
    if not ctx.command:
        return
    serverdata = r.table("blacklist").get(str(message.guild.id))
    if serverdata.run():
        commands = serverdata["commands"].map(lambda x: x["id"]).run()
        if str(ctx.command) in serverdata["disabled"].run():
            return
        if ctx.command.module[5:] in commands:
            blacklisted = list(filter(lambda x: x["id"] == ctx.command.module[5:], serverdata["commands"].run()))[0]["blacklisted"]
            if str(message.channel.id) in map(lambda x: x["id"], filter(lambda x: x["type"] == "channel", blacklisted)):
                return
            elif str(message.author.id) in map(lambda x: x["id"], filter(lambda x: x["type"] == "user", blacklisted)):
                return
            for x in message.author.roles:
                if str(x.id) in map(lambda x: x["id"], filter(lambda x: x["type"] == "role", blacklisted)):
                    return
        if str(ctx.command) in commands:
            blacklisted = list(filter(lambda x: x["id"] == str(ctx.command), serverdata["commands"].run()))[0]["blacklisted"]
            if str(message.channel.id) in map(lambda x: x["id"], filter(lambda x: x["type"] == "channel", blacklisted)):
                return
            elif str(message.author.id) in map(lambda x: x["id"], filter(lambda x: x["type"] == "user", blacklisted)):
                return
            for x in message.author.roles:
                if str(x.id) in map(lambda x: x["id"], filter(lambda x: x["type"] == "role", blacklisted)):
                    return
    if message.author.bot:
        return
    elif str(message.author.id) in r.table("blacklist").get("owner")["users"].run():
        return
    elif isinstance(message.channel, discord.abc.PrivateChannel) and message.content.startswith("s?"):
        await message.channel.send("You can't use commands in private messages :no_entry:")
        return
    else:
        await bot.process_commands(message)

@bot.event 
async def on_message_edit(before, after):
    await bot.wait_until_ready()
    if after.author.bot:
        return
    elif str(after.author.id) in r.table("blacklist").get("owner")["users"].run():
        return
    elif before.content == after.content:
        return
    elif isinstance(after.channel, discord.abc.PrivateChannel) and after.content.startswith("s?"):
        await after.channel.send("You can't use commands in private messages :no_entry:")
        return
    else:
        await bot.process_commands(after)
			
@bot.event
async def on_command_error(ctx, error, *args, **kwargs):
    channel = ctx.channel
    author = ctx.author 
    if isinstance(error, commands.CheckFailure):
        perms = ctx.command.checks[0]
        if ctx.command.checks[0].__name__ == "is_owner_check":
            try:
                ctx.command.reset_cooldown(ctx)
            except:
                pass
            return await channel.send("You do not have permission to use this command, Required permissions: Bot Owner :no_entry:")
        elif str(perms).split(" ")[1].split(".")[0] == "is_main_owner":
            try:
                ctx.command.reset_cooldown(ctx)
            except:
                pass
            return await channel.send("You do not have permission to use this command, Required permissions: Bot Owner :no_entry:")
        else:
            try:
                ctx.command.reset_cooldown(ctx)
            except:
                pass
            return await channel.send("You do not have permission to use this command, Required permissions: {} :no_entry:".format(", ".join(inspect.getclosurevars(ctx.command.checks[0]).nonlocals["perms"])))
    elif isinstance(error, commands.NoPrivateMessage):
        try:
            ctx.command.reset_cooldown(ctx)
        except:
            pass
        return await channel.send("This command cannot be used in DMs!")
    elif isinstance(error, commands.DisabledCommand):
        try:
            ctx.command.reset_cooldown(ctx)
        except:
            pass
        if not checks.is_owner_check(ctx):
            return await channel.send("The command `{}` has been disabled :no_entry:".format(ctx.command))
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
        try:
            perms = ctx.command.checks[0]
        except:
            perms = None
        msg = ""
        for x in ctx.command.params:
            if x != "ctx":
                if x != "self":
                    if "=" in str(ctx.command.params[x]):
                        msg += "[{}] ".format(x)
                    else:
                        msg += "<{}> ".format(x)
        if not ctx.command.aliases:
            aliases = "None"
        else:
            aliases = ", ".join([x for x in ctx.command.aliases])
        if not perms:
            msg = "Usage: {}{} {}\nCommand aliases: {}\nRequired permissions: None\nCommand description: {}".format(ctx.prefix, ctx.command, msg, aliases, ctx.command.help)
        else:
            msg = "Usage: {}{} {}\nCommand aliases: {}\nRequired permissions: {}\nCommand description: {}".format(ctx.prefix, ctx.command, msg, aliases, 
            ", ".join(inspect.getclosurevars(perms).nonlocals["perms"]) if perms.__name__ != "is_owner_check" and str(perms).split(" ")[1].split(".")[0] != "is_main_owner" else "Bot Owner", ctx.command.help)
        try:
            msg += "\n\nSub commands: {}".format(", ".join([x for x in ctx.command.all_commands if x not in ctx.command.all_commands[x].aliases]))
        except:
            pass
        s=discord.Embed(description=msg)
        s.set_author(name=ctx.command, icon_url=bot.user.avatar_url)
        await channel.send(embed=s)
        try:
            ctx.command.reset_cooldown(ctx)
        except:
            pass
        return
    elif isinstance(error, commands.CommandNotFound): 
        pass
    elif isinstance(error, commands.BadArgument):
        try:
            perms = ctx.command.checks[0]
        except:
            perms = None
        msg = ""
        for x in ctx.command.params:
            if x != "ctx":
                if x != "self":
                    if "=" in str(ctx.command.params[x]):
                        msg += "[{}] ".format(x)
                    else:
                        msg += "<{}> ".format(x)
        if not ctx.command.aliases:
            aliases = "None"
        else:
            aliases = ", ".join([x for x in ctx.command.aliases])
        if not perms:
            msg = "Usage: {}{} {}\nCommand aliases: {}\nRequired permissions: None\nCommand description: {}".format(ctx.prefix, ctx.command, msg, aliases, ctx.command.help)
        else:
            msg = "Usage: {}{} {}\nCommand aliases: {}\nRequired permissions: {}\nCommand description: {}".format(ctx.prefix, ctx.command, msg, aliases, 
            ", ".join(inspect.getclosurevars(perms).nonlocals["perms"]) if perms.__name__ != "is_owner_check" and str(perms).split(" ")[1].split(".")[0] != "is_main_owner" else "Bot Owner", ctx.command.help)
        try:
            msg += "\n\nSub commands: {}".format(", ".join([x for x in ctx.command.all_commands if x not in ctx.command.all_commands[x].aliases]))
        except:
            pass
        s=discord.Embed(description=msg)
        s.set_author(name=ctx.command, icon_url=bot.user.avatar_url)
        await channel.send(embed=s)
        try:
            ctx.command.reset_cooldown(ctx)
        except:
            pass
        return
    else:
        s=discord.Embed(title="Error", description="You have came across an error! [Support Server](https://discord.gg/PqJNcfB)\n{}".format(str(error)).replace("Command raised an exception: ", ""))
        await channel.send(embed=s)
        await bot.get_channel(439745234285625355).send("```Server: {}\nTime: {}\nCommand: {}\nAuthor: {}\n\n{}```".format(ctx.message.guild, datetime.datetime.utcnow().strftime("%d/%m/%Y %H:%M:%S"), ctx.command, ctx.message.author, str(error)))
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

async def on_error(self, event_method, *args, **kwargs):
    pass

bot.on_error = on_error
		
bot.add_cog(Main(bot))

bot.run(Token.bot())

