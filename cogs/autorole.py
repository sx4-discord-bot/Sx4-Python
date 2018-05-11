import discord
from discord.ext import commands
from utils.dataIO import dataIO
from utils import checks
import datetime
from collections import deque, defaultdict
import os
import re
import logging
import asyncio
import random
import time
import discord
from discord.ext import commands
from random import randint
from random import choice as randchoice
from discord.ext.commands import CommandNotFound
from utils.dataIO import fileIO


class Autorole:
    def __init__(self, bot):
        self.bot = bot
        self.JSON = "data/mod/autorole.json"
        self.data = dataIO.load_json(self.JSON)
		
    @commands.group(pass_context=True)
    async def autorole(self, ctx):
        """Allows a role to be added to a user when they join the server"""
        server = ctx.message.server
        if server.id not in self.data:
            self.data[server.id] = {}
            dataIO.save_json(self.JSON, self.data)
        if "role" not in self.data[server.id]:
            self.data[server.id]["role"] = {}
            dataIO.save_json(self.JSON, self.data)
        if "toggle" not in self.data[server.id]:
            self.data[server.id]["toggle"] = False
            dataIO.save_json(self.JSON, self.data)

    @autorole.command(pass_context=True) 
    @checks.admin_or_permissions(manage_roles=True)
    async def role(self, ctx, *, role: discord.Role):
        """Set the role to be added to a user whne they join"""
        server = ctx.message.server
        self.data[server.id]["role"] = role.name
        dataIO.save_json(self.JSON, self.data)
        await self.bot.say("The autorole role is now **{}** <:done:403285928233402378>".format(role.name))
		
    @autorole.command(pass_context=True)
    @checks.admin_or_permissions(manage_roles=True)
    async def fix(self, ctx):
        """Has the bot been offline and missed a few users? Use this to add the role to everyone who doesn't have it"""
        server = ctx.message.server
        role = discord.utils.get(server.roles, name=self.data[server.id]["role"])
        members = len([x for x in server.members if role not in x.roles])
        if not role:
            await self.bot.say("Role is not set or does not exist :no_entry:")
        for users in [x for x in server.members if role not in x.roles]:
            await self.bot.add_roles(users, role)
        await self.bot.say("Added **{}** to **{}** users <:done:403285928233402378>".format(role.name, members))
            
            
        
    @autorole.command(pass_context=True)
    @checks.admin_or_permissions(manage_roles=True)
    async def toggle(self, ctx):
        """Toggle autorole on or off"""
        server = ctx.message.server
        if self.data[server.id]["toggle"] == True:
            self.data[server.id]["toggle"] = False
            await self.bot.say("Auto-role has been **Disabled**")
            dataIO.save_json(self.JSON, self.data)
            return
        if self.data[server.id]["toggle"] == False:
            self.data[server.id]["toggle"] = True
            await self.bot.say("Auto-role has been **Enabled**")
            dataIO.save_json(self.JSON, self.data)
            return
		
    @autorole.command(pass_context=True)
    async def stats(self, ctx):
        """View the settings of autorole on your server"""
        server = ctx.message.server
        s=discord.Embed(colour=0xfff90d)
        s.set_author(name="Auto-role Settings", icon_url=self.bot.user.avatar_url)
        if self.data[server.id]["toggle"] == True:
            toggle = "Enabled"
        else:
            toggle = "Disabled"
        s.add_field(name="Status", value=toggle)
        if self.data[server.id]["role"] == {}:
            s.add_field(name="Auto-role role", value="Role not set")
        else:
            s.add_field(name="Auto-role role", value=self.data[server.id]["role"])
        await self.bot.say(embed=s)
			
    async def on_member_join(self, member):
        server = member.server
        role = discord.utils.get(server.roles, name=self.data[server.id]["role"])
        if self.data[server.id]["toggle"] == True: 
            await self.bot.add_roles(member, role)
			
def check_folders():
    if not os.path.exists("data/mod"):
        print("Creating data/mod folder...")
        os.makedirs("data/mod")

def check_files():
    s = "data/mod/autorole.json"
    if not dataIO.is_valid_json(s):
        print("Creating default mod's autorole.json...")
        dataIO.save_json(s, {})
		
def setup(bot): 
    check_folders()
    check_files()
    bot.add_cog(Autorole(bot))