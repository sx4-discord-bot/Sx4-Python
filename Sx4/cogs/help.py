import discord
from discord.ext import commands
import os
from copy import deepcopy
from collections import namedtuple, defaultdict, deque
from datetime import datetime
from random import randint
from copy import deepcopy
import inspect
from utils import checks
from enum import Enum
import time
import logging
import datetime
import math
from urllib.request import Request, urlopen
import json
from utils.PagedResult import PagedResult
from utils.PagedResult import PagedResultData
import random
from random import choice
import asyncio
from difflib import get_close_matches

class help:
    """help command"""

    def __init__(self, bot, connection):
        self.bot = bot
        self.db = connection
        
    @commands.command()
    async def help(self, ctx, commandname=None, *, subcommand=None):
        if not commandname and not subcommand:
            cogs = list(self.bot.cogs)
            economy = cogs.index("economy")
            cogs[0], cogs[economy] = cogs[economy], cogs[0]
            s=discord.Embed(colour=0xffff00)
            s.set_footer(text="s?help <command/module> for more info", icon_url=ctx.message.author.avatar_url)
            for cog in cogs:
                commands = ", ".join(sorted(["`" + command + "`" for command in self.bot.cogs[cog].bot.all_commands if self.bot.all_commands[command].module[5:].lower() == cog.lower() and self.bot.all_commands[command].hidden == False and command not in self.bot.all_commands[command].aliases], key=lambda x: x.lower()))
                commandsnum = len([x for x in self.bot.all_commands if self.bot.all_commands[x].hidden == False and x not in self.bot.all_commands[x].aliases])
                cogsnum = len([x for x in self.bot.all_commands if self.bot.all_commands[x].module[5:].lower() == cog.lower() and self.bot.all_commands[x].hidden == False and x not in self.bot.all_commands[x].aliases])
                s.set_author(name="Help ({} Commands)".format(commandsnum), icon_url=self.bot.user.avatar_url)
                if commands != "" and cog != "help":
                    s.add_field(name=cog.title() + " [{}]".format(cogsnum), value=commands, inline=False)
            await ctx.send(embed=s)
        elif not subcommand and commandname:
            msg = ""
            try:
                self.bot.all_commands[commandname.lower()] 
                try:
                    perms = self.bot.all_commands[commandname.lower()].checks[0]
                except:
                    perms = None
            except:
                try: 
                    cogcommandsnum = len("\n".join(["`{}` - {}".format(x, self.bot.cogs[commandname.lower()].bot.all_commands[x].help) for x in self.bot.cogs[commandname.lower()].bot.all_commands if self.bot.all_commands[x].module[5:].lower() == commandname.lower() and self.bot.all_commands[x].hidden == False and x not in self.bot.all_commands[x].aliases]))
                    pages = math.ceil(cogcommandsnum / 2000)
                    commandnumber = len([x for x in self.bot.cogs[commandname.lower()].bot.all_commands if self.bot.all_commands[x].module[5:].lower() == commandname.lower() and self.bot.all_commands[x].hidden == False and x not in self.bot.all_commands[x].aliases])
                    cogcommands = "\n".join(sorted(["`{}` - {}".format(x, self.bot.cogs[commandname.lower()].bot.all_commands[x].help) for x in self.bot.cogs[commandname.lower()].bot.all_commands if self.bot.all_commands[x].module[5:].lower() == commandname.lower() and self.bot.all_commands[x].hidden == False and x not in self.bot.all_commands[x].aliases], key=lambda x: x))
                    n = 0
                    m = 2000
                    for x in range(pages):
                        if n != 0:
                            while cogcommands[n-1:n] != "\n":
                                n -= 1
                        while cogcommands[m-1:m] != "\n":
                            m -= 1
                        s=discord.Embed(colour=0xffff00, description=cogcommands[n:m])
                        if n == 0:
                            s.set_author(name=commandname.title() + " ({} Commands)".format(commandnumber), icon_url=self.bot.user.avatar_url)
                        s.set_footer(text="s?help <command> for more info", icon_url=ctx.message.author.avatar_url)
                        n += 2000
                        m += 2000
                        await ctx.send(embed=s)
                    return
                except:
                    await ctx.send("That is not a valid command or module :no_entry:")
                    return
            if not self.bot.all_commands[commandname.lower()].usage:
                for x in self.bot.all_commands[commandname.lower()].params:
                    if x != "ctx":
                        if x != "self":
                            if "=" in str(self.bot.all_commands[commandname.lower()].params[x]):
                                msg += "[{}] ".format(x)
                            else:
                                msg += "<{}> ".format(x)
            else:
                msg += self.bot.all_commands[commandname.lower()].usage
            if not self.bot.all_commands[commandname.lower()].aliases:
                aliases = "None"
            else:
                aliases = ", ".join([x for x in self.bot.all_commands[commandname.lower()].aliases])
            if not perms:
                msg = "Usage: {}{} {}\nCommand aliases: {}\nRequired permissions: None\nCommand description: {}".format(ctx.prefix, self.bot.all_commands[commandname.lower()], msg, aliases, self.bot.all_commands[commandname.lower()].help)
            else:
                msg = "Usage: {}{} {}\nCommand aliases: {}\nRequired permissions: {}\nCommand description: {}".format(ctx.prefix, self.bot.all_commands[commandname.lower()], msg, aliases, 
                ", ".join(inspect.getclosurevars(perms).nonlocals["perms"]) if perms.__name__ != "is_owner_check" and str(perms).split(" ")[1].split(".")[0] != "is_main_owner" else "Bot Owner", self.bot.all_commands[commandname.lower()].help)
            try:
                msg += "\n\nSub commands: {}".format(", ".join([x for x in self.bot.all_commands[commandname.lower()].all_commands if x not in self.bot.all_commands[commandname.lower()].all_commands[x].aliases]))
            except:
                pass
            s=discord.Embed(description=msg)
            s.set_author(name=self.bot.all_commands[commandname.lower()].name, icon_url=self.bot.user.avatar_url)
            await ctx.send(embed=s)
        else:
            msg = ""
            try:
                self.bot.all_commands[commandname.lower()].all_commands[subcommand.lower()] 
                try:
                    perms = self.bot.all_commands[commandname.lower()].all_commands[subcommand.lower()].checks[0]
                except:
                    perms = None
            except:
               await ctx.send("That is not a command :no_entry:")
               return
            if not self.bot.all_commands[commandname.lower()].all_commands[subcommand.lower()].usage:
                for x in self.bot.all_commands[commandname.lower()].all_commands[subcommand.lower()].params:
                    if x != "ctx":
                        if x != "self":
                            if "=" in str(self.bot.all_commands[commandname.lower()].all_commands[subcommand.lower()].params[x]):
                                msg += "[{}] ".format(x)
                            else:
                                msg += "<{}> ".format(x)
            else:
                msg += self.bot.all_commands[commandname.lower()].all_commands[subcommand.lower()].usage
            if not self.bot.all_commands[commandname.lower()].all_commands[subcommand.lower()].aliases:
                aliases = "None"
            else:
                aliases = ", ".join([x for x in self.bot.all_commands[commandname.lower()].all_commands[subcommand.lower()].aliases])
            if not perms:
                msg = "Usage: {}{} {}\nCommand aliases: {}\nRequired permissions: None\nCommand description: {}".format(ctx.prefix, self.bot.all_commands[commandname.lower()].all_commands[subcommand.lower()], msg, aliases, self.bot.all_commands[commandname.lower()].all_commands[subcommand.lower()].help)
            else:
                msg = "Usage: {}{} {}\nCommand aliases: {}\nRequired permissions: {}\nCommand description: {}".format(ctx.prefix, self.bot.all_commands[commandname.lower()].all_commands[subcommand.lower()], msg, aliases, 
                ", ".join(inspect.getclosurevars(perms).nonlocals["perms"]) if perms.__name__ != "is_owner_check" and str(perms).split(" ")[1].split(".")[0] != "is_main_owner" else "Bot Owner", self.bot.all_commands[commandname.lower()].all_commands[subcommand.lower()].help)
            s=discord.Embed(description=msg)
            s.set_author(name=self.bot.all_commands[commandname.lower()].name + " " + self.bot.all_commands[commandname.lower()].all_commands[subcommand.lower()].name, icon_url=self.bot.user.avatar_url)
            await ctx.send(embed=s)
            
def setup(bot, connection):
    n = help(bot, connection)
    bot.remove_command('help')
    bot.add_cog(n)
