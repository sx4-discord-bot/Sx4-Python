import discord
import asyncio
from discord.ext import commands
from random import choice as randchoice
import time
import datetime
import random
from utils import checks
import os
from random import choice
from utils.dataIO import dataIO
from random import randint
from copy import deepcopy
from collections import namedtuple, defaultdict, deque
from copy import deepcopy
from enum import Enum
import asyncio
from difflib import get_close_matches

class Afk:
    def __init__(self, bot):
        self.bot = bot
        self.json = "data/afk/settings.json"
        self.data = dataIO.load_json(self.json)
		
    @commands.command(pass_context=True, aliases=["away"])
    async def afk(self, ctx, *, message=None):
        author = ctx.message.author
        server = ctx.message.server
        if "server" not in self.data:
            self.data["server"] = {}
            dataIO.save_json(self.json, self.data)
        if server.id not in self.data["server"]:
            self.data["server"][server.id] = {}
            dataIO.save_json(self.json, self.data)
        if "toggle" not in self.data["server"][server.id]:
            self.data["server"][server.id]["toggle"] = True
            dataIO.save_json(self.json, self.data)
        if "user" not in self.data:
            self.data["user"] = {}
            dataIO.save_json(self.json, self.data)
        if author.id not in self.data["user"]:
            self.data["user"][author.id] = {}
            dataIO.save_json(self.json, self.data)
        if "message" not in self.data["user"][author.id]:
            self.data["user"][author.id]["message"] = None
            dataIO.save_json(self.json, self.data)
        if "toggle" not in self.data["user"][author.id]:
            self.data["user"][author.id]["toggle"] = False
            dataIO.save_json(self.json, self.data)
        if "nickbefore" not in self.data["user"][author.id]:
            self.data["user"][author.id]["nickbefore"] = {}
            dataIO.save_json(self.json, self.data)
        if self.data["server"][server.id]["toggle"] == False:
            await self.bot.say("AFK messages are disabled on this server :no_entry:")
            return
        if message:
            if "http://" in message.lower() or "https://" in message.lower() or "discord.gg" in message.lower() or ".com" in message.lower() or "www." in message.lower():
                await self.bot.say("No advertising in your AFK message :no_entry:")
                return
            self.data["user"][author.id]["message"] = message
        if self.data["user"][author.id]["toggle"] == False:
            self.data["user"][author.id]["toggle"] = True
            self.data["user"][author.id]["nickbefore"] = author.display_name
            try:
                await self.bot.change_nickname(author, "{} [AFK]".format(author.display_name))
            except:
                pass
            dataIO.save_json(self.json, self.data)
            await self.bot.say("You are now AFK :wave:")
            return
        if self.data["user"][author.id]["toggle"] == True:
            self.data["user"][author.id]["toggle"] = False
            del self.data["user"][author.id]["message"]
            try:
                await self.bot.change_nickname(author, self.data["user"][author.id]["nickbefore"])
            except:
                pass
            dataIO.save_json(self.json, self.data)
            await self.bot.say("You are now back :wave:")
            return
			
    @commands.command(pass_context=True)
    @checks.admin_or_permissions(manage_messages=True)
    async def toggleafk(self, ctx):
        server = ctx.message.server
        if "server" not in self.data:
            self.data["server"] = {}
            dataIO.save_json(self.json, self.data)
        if server.id not in self.data["server"]:
            self.data["server"][server.id] = {}
            dataIO.save_json(self.json, self.data)
        if "toggle" not in self.data["server"][server.id]:
            self.data["server"][server.id]["toggle"] = True
            dataIO.save_json(self.json, self.data)
        if self.data["server"][server.id]["toggle"] == True:
            self.data["server"][server.id]["toggle"] = False
            dataIO.save_json(self.json, self.data)
            await self.bot.say("AFK messages are now disabled in this server <:done:403285928233402378>")
            return
        if self.data["server"][server.id]["toggle"] == False:
            self.data["server"][server.id]["toggle"] = True
            dataIO.save_json(self.json, self.data)
            await self.bot.say("AFK messages are now enabled in this server <:done:403285928233402378>")
            return
			
    async def on_message(self, message):
        server = message.server
        if self.data["server"][server.id]["toggle"] == False:
            return
					
def check_folders():
    if not os.path.exists("data/afk"):
        print("Creating data/afk folder...")
        os.makedirs("data/afk")


def check_files():
    f = 'data/afk/settings.json'
    if not dataIO.is_valid_json(f):
        dataIO.save_json(f, {})
        print('Creating default rps.json...')
		
def setup(bot):
    check_folders()
    check_files()
    bot.add_cog(Afk(bot))
        