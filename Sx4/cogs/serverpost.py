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
from cogs import mod
from utils import Token
import aiohttp
import json
import traceback
import sys
import os
import subprocess

dbltoken = Token.dbl()
dbotspwtoken = Token.dbpw()
botspacetoken = Token.botlistspace()
dbpwurl = "https://discord.bots.gg/api/v1/bots/440996323156819968/stats"
url = "https://discordbots.org/api/bots/440996323156819968/stats"
botspaceurl = "https://api.botlist.space/v1/bots/440996323156819968/"
headers = {"Authorization" : dbltoken}
headersdb = {"Authorization" : dbotspwtoken, "Content-Type" : "application/json"}
headersbs = {"Authorization" : botspacetoken, "Content-Type" : "application/json"}

class serverpost:
    def __init__(self, bot, connection):
        self.bot = bot
        self.db = connection
        self.task = bot.loop.create_task(self.server_post())

    def __unload(self):
        self.task.cancel()

    @commands.command(hidden=True)
    @checks.is_owner()
    async def post(self, ctx):
        dblpayloadservers = {"server_count": len(self.bot.guilds), "shard_count": self.bot.shard_count}
        payloadservers = {"server_count": len(self.bot.guilds), "shards": self.bot.shard_count}
        dbpwpayload = {"guildCount": len(self.bot.guilds), "shardCount": self.bot.shard_count}
        s=discord.Embed()
        s.set_author(name="Server Count Posting", icon_url=self.bot.user.avatar_url)
        try:
            requests.post(url, data=dblpayloadservers, headers=headers)
            s.add_field(name="Discord Bot List", value="Posted")
        except Exception as e: 
            s.add_field(name="Discord Bot List", value=e)
        try:
            requests.post(dbpwurl, data=dbpwpayload, headers=headersdb)
            s.add_field(name="Discord Bots.pw", value="Posted")
        except Exception as e: 
            s.add_field(name="Discord Bots.pw", value=e)
        try:
            requests.post(botspaceurl, data=json.dumps(payloadservers), headers=headersbs)
            s.add_field(name="BotList.Space", value="Posted")
        except Exception as e: 
            s.add_field(name="BotList.Space", value=e)
        await ctx.send(embed=s)


    async def server_post(self):
        while not self.bot.is_closed():
            dblpayloadservers = {"server_count": len(self.bot.guilds), "shard_count": self.bot.shard_count}
            payloadservers = {"server_count": len(self.bot.guilds), "shards": self.bot.shard_count}
            dbpwpayload = {"guildCount": len(self.bot.guilds), "shardCount": self.bot.shard_count}
            try:
                requests.post(url, data=dblpayloadservers, headers=headers)
            except: 
                pass
            try:
                requests.post(dbpwurl, data=json.dumps(dbpwpayload), headers=headersdb)
            except: 
                pass
            try:
                requests.post(botspaceurl, data=json.dumps(payloadservers), headers=headersbs)
            except:
                pass
            await asyncio.sleep(3600)

def setup(bot, connection):
    bot.add_cog(serverpost(bot, connection))