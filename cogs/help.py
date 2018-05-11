import discord
from discord.ext import commands
import os
from copy import deepcopy
from utils.dataIO import dataIO
from collections import namedtuple, defaultdict, deque
from datetime import datetime
from random import randint
from copy import deepcopy
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

class Help:
    """help command"""

    def __init__(self, bot):
        self.bot = bot
        
    @commands.command(pass_context=True)
    async def help(self, ctx, commandname=None, *, subcommand=None):
        if not commandname and not subcommand:
            s=discord.Embed(colour=0xffff00)
            s.set_footer(text="s?help <command> for more info", icon_url=ctx.message.author.avatar_url)
            for cog in self.bot.cogs:
                commands = ", ".join(["`" + command + "`" for command in self.bot.cogs[cog].bot.commands if self.bot.commands[command].module.__name__[5:].lower() == cog.lower() and self.bot.commands[command].hidden == False and command not in self.bot.commands[command].aliases])
                commandsnum = len([x for x in self.bot.commands if self.bot.commands[x].hidden == False and x not in self.bot.commands[x].aliases])
                s.set_author(name="Help ({} Commands)".format(commandsnum), icon_url=self.bot.user.avatar_url)
                if commands != "" and cog != "music" and cog != "Help":
                    s.add_field(name=cog.title(), value=commands, inline=False)
            s.add_field(name="Welcomer", value="`welcomer`", inline=False)
            await self.bot.say(embed=s)
        elif not subcommand and commandname:
            msg = ""
            try:
               self.bot.commands[commandname.lower()] 
            except:
               await self.bot.say("That is not a command :no_entry:")
               return
            for x in self.bot.commands[commandname.lower()].params:
                if x != "ctx":
                    if x != "self":
                        if "None" in str(self.bot.commands[commandname.lower()].params[x]):
                            msg += "[{}] ".format(x)
                        else:
                            msg += "<{}> ".format(x)
            if not self.bot.commands[commandname.lower()].aliases:
                aliases = "None"
            else:
                aliases = ", ".join([x for x in self.bot.commands[commandname.lower()].aliases])
            msg = "Usage: {}{} {}\nCommand aliases: {}\nCommand description: {}".format(ctx.prefix, self.bot.commands[commandname.lower()].name, msg, aliases, self.bot.commands[commandname.lower()].help)
            try:
                msg += "\n\nSub commands: {}".format(", ".join([x for x in self.bot.commands[commandname.lower()].commands if x not in self.bot.commands[commandname.lower()].commands[x].aliases]))
            except:
                pass
            s=discord.Embed(description=msg)
            s.set_author(name=self.bot.commands[commandname.lower()].name, icon_url=self.bot.user.avatar_url)
            await self.bot.say(embed=s)
        else:
            msg = ""
            try:
               self.bot.commands[commandname.lower()].commands[subcommand.lower()] 
            except:
               await self.bot.say("That is not a command :no_entry:")
               return
            for x in self.bot.commands[commandname.lower()].commands[subcommand.lower()].params:
                if x != "ctx":
                    if x != "self":
                        if "None" in str(self.bot.commands[commandname.lower()].commands[subcommand.lower()].params[x]):
                            msg += "[{}] ".format(x)
                        else:
                            msg += "<{}> ".format(x)
            if not self.bot.commands[commandname.lower()].commands[subcommand.lower()].aliases:
                aliases = "None"
            else:
                aliases = ", ".join([x for x in self.bot.commands[commandname.lower()].commands[subcommand.lower()].aliases])
            msg = "Usage: {}{} {} {}\nCommand aliases: {}\nCommand description: {}".format(ctx.prefix, self.bot.commands[commandname.lower()].name, self.bot.commands[commandname.lower()].commands[subcommand.lower()].name, msg, aliases, self.bot.commands[commandname.lower()].commands[subcommand.lower()].help)
            s=discord.Embed(description=msg)
            s.set_author(name=self.bot.commands[commandname.lower()].name + " " + self.bot.commands[commandname.lower()].commands[subcommand.lower()].name, icon_url=self.bot.user.avatar_url)
            await self.bot.say(embed=s)
            
def setup(bot):
    n = Help(bot)
    bot.remove_command('help')
    bot.add_cog(n)
