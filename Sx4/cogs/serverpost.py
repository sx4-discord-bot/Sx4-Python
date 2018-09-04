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
konomitoken = Token.konomi()
dbpwurl = "https://bots.discord.pw/api/bots/440996323156819968/stats"
url = "https://discordbots.org/api/bots/440996323156819968/stats"
botspaceurl = "https://botlist.space/api/bots/440996323156819968/"
konomiurl = "http://bots.disgd.pw/api/bot/440996323156819968/stats"
headers = {"Authorization" : dbltoken}
headersdb = {"Authorization" : dbotspwtoken, "Content-Type" : "application/json"}
headerskon = {"Authorization" : konomitoken, "Content-Type" : "application/json"}
headersbs = {"Authorization" : botspacetoken, "Content-Type" : "application/json"}

class serverpost:
    def __init__(self, bot):
        self.bot = bot
        self.task = bot.loop.create_task(self.server_post())

    def __unload(self):
        self.task.cancel()

    @commands.command(hidden=True)
    @checks.is_owner()
    async def post(self, ctx):
        dblpayloadservers = {"server_count"  : len(self.bot.guilds), "shard_count": self.bot.shard_count}
        payloadservers = {"server_count"  : len(self.bot.guilds)}
        s=discord.Embed()
        s.set_author(name="Server Count Posting", icon_url=self.bot.user.avatar_url)
        try:
            requests.post(url, data=dblpayloadservers, headers=headers)
            s.add_field(name="Discord Bot List", value="Posted")
        except Exception as e: 
            s.add_field(name="Discord Bot List", value=e)
        try:
            requests.post(dbpwurl, data=json.dumps(payloadservers), headers=headersdb)
            s.add_field(name="Discord Bots.pw", value="Posted")
        except Exception as e: 
            s.add_field(name="Discord Bots.pw", value=e)
        try:
            requests.post(botspaceurl, data=json.dumps(payloadservers), headers=headersbs)
            s.add_field(name="BotList.Space", value="Posted")
        except Exception as e: 
            s.add_field(name="BotList.Space", value=e)
        try:
            requests.post(konomiurl, data=json.dumps({"guild_count" : len(self.bot.guilds)}), headers=headerskon)
            s.add_field(name="Konomi Bots", value="Posted")
        except Exception as e: 
            s.add_field(name="Konomi Bots", value=e)
        await ctx.send(embed=s)


    async def server_post(self):
        while not self.bot.is_closed():
            dblpayloadservers = {"server_count"  : len(self.bot.guilds), "shard_count": self.bot.shard_count}
            payloadservers = {"server_count"  : len(self.bot.guilds)}
            try:
                requests.post(url, data=dblpayloadservers, headers=headers)
            except: 
                pass
            try:
                requests.post(dbpwurl, data=json.dumps(payloadservers), headers=headersdb)
            except: 
                pass
            try:
                requests.post(botspaceurl, data=json.dumps(payloadservers), headers=headersbs)
            except:
                pass
            try:
                requests.post(konomiurl, data=json.dumps({"guild_count" : len(self.bot.guilds)}), headers=headerskon)
            except: 
                pass
            await asyncio.sleep(3600)

def setup(bot):
    bot.add_cog(serverpost(bot))