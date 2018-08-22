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
from utils import arghelp
import discord
from discord.ext import commands
from random import randint
from random import choice as randchoice
from discord.ext.commands import CommandNotFound
from utils.dataIO import fileIO


class autorole:
    def __init__(self, bot):
        self.bot = bot
        self.JSON = "data/mod/autorole.json"
        self.data = dataIO.load_json(self.JSON)
		
    @commands.group()
    async def autorole(self, ctx):
        """Allows a role to be added to a user when they join the server"""
        server = ctx.guild
        if ctx.invoked_subcommand is None:
            await arghelp.send(self.bot, ctx)
        else:
            if str(server.id) not in self.data:
                self.data[str(server.id)] = {}
                dataIO.save_json(self.JSON, self.data)
            if "role" not in self.data[str(server.id)]:
                self.data[str(server.id)]["role"] = {}
                dataIO.save_json(self.JSON, self.data)
            if "toggle" not in self.data[str(server.id)]:
               self.data[str(server.id)]["toggle"] = False
               dataIO.save_json(self.JSON, self.data)

    @autorole.command() 
    @checks.has_permissions("manage_roles")
    async def role(self, ctx, *, role: discord.Role):
        """Set the role to be added to a user whne they join"""
        server = ctx.guild
        self.data[str(server.id)]["role"] = role.id
        dataIO.save_json(self.JSON, self.data)
        await ctx.send("The autorole role is now **{}** <:done:403285928233402378>".format(role.name))
		
    @autorole.command()
    @checks.has_permissions("manage_roles")
    async def fix(self, ctx, subarg=None):
        """Has the bot been offline and missed a few users? Use this to add the role to everyone who doesn't have it"""
        server = ctx.guild
        if not subarg:
            users = server.members
        elif subarg.lower() == "nobots":
            users = filter(lambda m: not m.bot, server.members)
        elif subarg.lower() == "bots":
            users = filter(lambda m: m.bot, server.members)
        role = discord.utils.get(server.roles, id=self.data[str(server.id)]["role"])
        if not role:
            return await ctx.send("You need to set the autorole before you can use this :no_entry:")
        members = len([x for x in users if role not in x.roles])
        if not role:
            await ctx.send("Role is not set or does not exist :no_entry:")
        i = 0
        for user in [x for x in users if role not in x.roles]:
            try:
                await user.add_roles(role, reason="Autorole fix")
                i += 1
            except:
                pass
        msg = ", I was unable to add the role to **{}** users".format(members - i)
        await ctx.send("Added **{}** to **{}** users{} <:done:403285928233402378>".format(role.name, i, msg if members != i else ""))
            
            
        
    @autorole.command()
    @checks.has_permissions("manage_roles")
    async def toggle(self, ctx):
        """Toggle autorole on or off"""
        server = ctx.guild
        if self.data[str(server.id)]["toggle"] == True:
            self.data[str(server.id)]["toggle"] = False
            await ctx.send("Auto-role has been **Disabled**")
            dataIO.save_json(self.JSON, self.data)
            return
        if self.data[str(server.id)]["toggle"] == False:
            self.data[str(server.id)]["toggle"] = True
            await ctx.send("Auto-role has been **Enabled**")
            dataIO.save_json(self.JSON, self.data)
            return
		
    @autorole.command()
    async def stats(self, ctx):
        """View the settings of autorole on your server"""
        server = ctx.guild
        s=discord.Embed(colour=0xfff90d)
        s.set_author(name="Auto-role Settings", icon_url=self.bot.user.avatar_url)
        if self.data[str(server.id)]["toggle"] == True:
            toggle = "Enabled"
        else:
            toggle = "Disabled"
        s.add_field(name="Status", value=toggle)
        if self.data[str(server.id)]["role"] == {}:
            s.add_field(name="Auto-role role", value="Role not set")
        else:
            s.add_field(name="Auto-role role", value=discord.utils.get(ctx.guild.roles, id=self.data[str(server.id)]["role"]).name)
        await ctx.send(embed=s)
			
    async def on_member_join(self, member):
        server = member.guild
        role = discord.utils.get(server.roles, id=self.data[str(server.id)]["role"])
        if self.data[str(server.id)]["toggle"] == True: 
            await member.add_roles(role, reason="Autorole")
			
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
    bot.add_cog(autorole(bot))