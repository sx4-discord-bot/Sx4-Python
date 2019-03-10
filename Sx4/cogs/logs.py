import discord
from discord.ext import commands
from utils import checks
from datetime import datetime
from collections import deque, defaultdict
import os
import re
from . import owner as dev
import logging
import asyncio
import rethinkdb as r
import random
from utils import arghelp
import time
import discord
from discord.ext import commands
from random import randint
from random import choice as randchoice
from discord.ext.commands import CommandNotFound

class logs:
    def __init__(self, bot, connection):
        self.bot = bot
        self.db = connection
		
    @commands.group(usage="<sub command>")
    async def logs(self, ctx):
        """Log actions in your server"""
        server = ctx.guild
        if ctx.invoked_subcommand is None:
            await arghelp.send(self.bot, ctx)
        else:
            r.table("logs").insert({"id": str(server.id), "channel": None, "toggle": False}).run(self.db, durability="soft")
		
    @logs.command()
    @checks.has_permissions("manage_guild")
    async def channel(self, ctx, channel: discord.TextChannel=None):
        """Set the channel where you want stuff to be logged"""
        server = ctx.guild
        serverdata = r.table("logs").get(str(server.id))
        if not channel:
            channel = ctx.message.channel
        serverdata.update({"channel": str(channel.id)}).run(self.db, durability="soft")
        await ctx.send("Logs will be recorded in <#{}> if toggled on <:done:403285928233402378>".format(channel.id))
		
    @logs.command()
    @checks.has_permissions("manage_guild")
    async def toggle(self, ctx):
        """Toggle logs on or off"""
        server = ctx.guild
        serverdata = r.table("logs").get(str(server.id))
        if serverdata["toggle"].run(self.db, durability="soft") == False:
            serverdata.update({"toggle": True}).run(self.db, durability="soft")
            await ctx.send("Logs have been toggled **on** <:done:403285928233402378>")
            return
        if serverdata["toggle"].run(self.db, durability="soft") == True:
            serverdata.update({"toggle": False}).run(self.db, durability="soft")
            await ctx.send("Logs have been toggled **off** <:done:403285928233402378>")
            return

    @logs.command()
    async def stats(self, ctx):
        server = ctx.guild
        serverdata = r.table("logs").get(str(server.id)).run(self.db, durability="soft")
        s=discord.Embed(colour=0xffff00)
        s.set_author(name="Logs Settings", icon_url=self.bot.user.avatar_url)
        s.add_field(name="Status", value="Enabled" if serverdata["toggle"] else "Disabled")
        s.add_field(name="Channel", value=server.get_channel(int(serverdata["channel"])).mention if serverdata["channel"] and server.get_channel(int(serverdata["channel"])) else "Not set")
        await ctx.send(embed=s)

def setup(bot, connection): 
    bot.add_cog(logs(bot, connection))